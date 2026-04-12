"""
戶外行動版 Web 伺服器主程式 (Web_Main)
提供 FastAPI 作為接收手機端畫面與提供網頁的後端口
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import base64
import numpy as np
import cv2
import uvicorn
import os
import sys
import time

from agent.navigation_agent import NavigationAgent
from audio.voice_interface import VoiceInterface
from vision.vision_analyzer import VisionAnalyzer

app = FastAPI(title="Vision Nav Mobile API")
# 初始化 OpenClaw 決策大腦
agent = NavigationAgent()
voice = VoiceInterface()
vision_analyzer = VisionAnalyzer()

class ImagePayload(BaseModel):
    image_b64: str

class CommandPayload(BaseModel):
    command: str

class PhotoCommandPayload(BaseModel):
    """拍照指令：包含語音辨識文字和截圖"""
    text: str
    image_b64: str

@app.get("/")
async def get_index():
    """回傳給手機端的前端 UI 介面"""
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/analyze")
def analyze_frame(payload: ImagePayload):
    """
    接收手機發來的 Base64 照片字串，傳給大腦分析。
    使用 def (而非 async def) 讓 FastAPI 自動將耗時任務放入 ThreadPool 中，避免卡死伺服器！
    """
    start_t = time.time()
    try:
        b64_img = payload.image_b64
        if not b64_img:
            return {"warning": "沒有接收到影像資料"}

        img_bytes = base64.b64decode(b64_img)
        np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        print(f"[效能診斷] 1. 前端影像接收與解碼完畢: {time.time() - start_t:.2f} 秒")
        
        t_yolo = time.time()
        visual_data = {"frame": frame}
        decision = agent.analyze_environment(visual_data)
        
        print(f"[效能診斷] 2. 總決策花費時間 (YOLO + OpenClaw): {time.time() - t_yolo:.2f} 秒")
        print(f"[效能診斷] =========================================")
        
        return {
            "warning": decision.get("warning"),
            "action": decision.get("action")
        }
        
    except Exception as e:
        return {"warning": f"電腦端系統錯誤: {str(e)}"}

@app.post("/api/photo")
async def process_photo_command(payload: PhotoCommandPayload):
    """
    接收截圖 + 語音指令，進行商品辨識
    """
    print(f"\n[📸 收到拍照指令] 文字: {payload.text}")
    voice.speak("收到，正在分析商品")

    try:
        # 解碼圖片
        img_bytes = base64.b64decode(payload.image_b64)
        np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            voice.speak("無法解讀圖片")
            return {"reply": "無法解讀圖片", "text": payload.text}

        result = vision_analyzer.send_photo(frame)
        if result:
            # 【優化】根據不同回傳格式調整回覆內容
            if isinstance(result, dict) and "product_name" in result:
                summary = result.get("summary", "")
                price = result.get("price", "")
                reply = f"已找到商品：{result['product_name']}，價格{price}元，{summary}"
            elif isinstance(result, dict) and "raw" in result:
                reply = f"已找到商品：{result['raw']}"
            else:
                reply = f"已找到商品：{result}"

            voice.speak(reply)

            # 【修復】發送到 Telegram
            # openclaw CLI 會因為輸出 Unicode emoji 而卡住，故用 start /b 在背景執行
            import os
            try:
                telegram_msg = (
                    f"🛒 已找到商品：{result.get('product_name', reply)}\n"
                    f"💰 價格：{result.get('price', '未知')}元\n"
                    f"⭐ 評價：{result.get('reviews', '未知')}\n"
                    f"🔗 購買連結：{result.get('link', '無')}"
                )
                # 使用 start /b 在背景執行，不等待輸出，避免 Unicode 编码卡住
                cmd = f'start /b /wait cmd.exe /c openclaw message send --channel telegram --target "8603543691" --message "{telegram_msg}"'
                os.system(cmd)
            except Exception as te:
                print(f"[📸 Telegram 發送失敗] {te}")

            return {"reply": reply, "text": payload.text, "photo_result": result}
        else:
            voice.speak("無法辨識商品，請稍後再試")
            return {"reply": "無法辨識商品", "text": payload.text}

    except Exception as e:
        print(f"[📸 拍照處理失敗] {e}")
        voice.speak("圖片處理失敗")
        return {"reply": f"處理失敗：{str(e)}", "text": payload.text}

@app.post("/api/command_audio")
async def process_audio_command(request: Request):
    """
    (新版) 接收前端純 JS 編碼的 WAV 音軌二進制檔案，後端直接送 Google STT
    若語音包含「拍照」，則拍攝無壓縮圖片傳送給 OpenClaw 進行商品辨識
    """
    audio_data = await request.body()
    print(f"\n[⬇️ 伺服器收到純音訊] 大小: {len(audio_data)} bytes")

    import speech_recognition as sr
    import io

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_data)) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="zh-TW")

            print(f"\n" + "!"*40)
            print(f"[🔴 後端錄音直出解析結果] 🗣️: {text}")
            print("!"*40 + "\n")

            # 檢查是否包含「拍照」關鍵字
            if "拍照" in text or "拍一張" in text:
                print("[📸 偵測到拍照指令] 請發送截圖...")
                voice.speak("收到，請發送截圖")
                return {"reply": "收到拍照指令，請發送截圖", "text": text, "need_photo": True}
            else:
                # 一般指令
                voice.speak(f"收到指令：{text}")
                return {"reply": f"系統收到指令：{text}", "text": text}

    except sr.UnknownValueError:
        print("[🔴 後端辨識失敗] 聽不清楚或沒有講話")
        return {"reply": "聽不清楚，請再講一次", "text": ""}
    except Exception as e:
        print(f"[🔴 後端辨識異常] {e}")
        return {"reply": "連線辨識系統失敗", "text": ""}

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" 🚀 戶外微服務伺服器已啟動 ...")
    print(" 【下一步請執行】在電腦的其他終端機執行：")
    print("                 ngrok http 8000")
    print(" 然後用手機打開 ngrok 產生的 https 網址！")
    print("="*50 + "\n")
    # 開啟 FastAPI 在 8000 Port
    uvicorn.run(app, host="0.0.0.0", port=8000)
