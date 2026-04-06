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

# 讓系統找得到同一個資料夾下的其他模組
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.agent.navigation_agent import NavigationAgent

app = FastAPI(title="Vision Nav Mobile API")
# 初始化 OpenClaw 決策大腦
agent = NavigationAgent()

class ImagePayload(BaseModel):
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
        
        print(f"[效能診斷] 2. 總決策花費時間 (YOLO + Ollama): {time.time() - t_yolo:.2f} 秒")
        print(f"[效能診斷] =========================================")
        
        return {
            "warning": decision.get("warning"),
            "action": decision.get("action")
        }
        
    except Exception as e:
        return {"warning": f"電腦端系統錯誤: {str(e)}"}

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" 🚀 戶外微服務伺服器已啟動 ...")
    print(" 【下一步請執行】在電腦的其他終端機執行：")
    print("                 ngrok http 8000")
    print(" 然後用手機打開 ngrok 產生的 https 網址！")
    print("="*50 + "\n")
    # 開啟 FastAPI 在 8000 Port
    uvicorn.run(app, host="0.0.0.0", port=8000)
