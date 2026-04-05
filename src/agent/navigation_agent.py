"""
OpenClaw Navigation Agent
AI 決策大腦，負責環境感知與導航決策 (透過 REST API 串接本地 OpenClaw 伺服器)
"""
import logging
import time
import os
import cv2
import yaml
import base64
import requests

logger = logging.getLogger(__name__)

class NavigationAgent:
    """
    導航 Agent
    接收視覺辨識結果，透過 HTTP 請求發送給本地 OpenClaw 伺服器
    """
    
    def __init__(self):
        self.last_api_call = 0
        self.cooldown_seconds = 3.0  # 設定每次 API 呼叫的間隔秒數
        
        # 讀取 config
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                ai_config = config.get('ai', {})
                self.endpoint = ai_config.get('endpoint', 'http://127.0.0.1:18789/api/generate')
                self.model_name = ai_config.get('model', 'gemini')
        except Exception:
            self.endpoint = 'http://127.0.0.1:18789/api/generate'
            self.model_name = 'gemini'

        logger.info(f"NavigationAgent initialized. Endpoint: {self.endpoint}, Model: {self.model_name}")

    def analyze_environment(self, visual_data: dict) -> dict:
        """
        分析環境資料，輸出導航建議
        """
        frame = visual_data.get("frame")
        if frame is None:
            return {"action": "forward", "warning": None, "confidence": 0.0}

        # 冷卻時間檢查，避免過度頻繁打 API
        current_time = time.time()
        if (current_time - self.last_api_call) < self.cooldown_seconds:
            return {"action": "forward", "warning": None, "confidence": 0.0, "cooldown": True}
            
        self.last_api_call = current_time

        try:
            # 將 OpenCV 畫面壓縮並編碼為 JPG Base64，減少傳輸負載
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            prompt = (
                "你現在是一個視障者的安全導航助手。請看這張前方攝影機的即時畫面。"
                "如果有危險（例如正前方有障礙物、階梯、水坑、電線等），請用『一句話』簡潔說明重點障礙物與建議方向（例如：『前方有沙發，請靠右走』）。"
                "如果前方安全無障礙，請直接回答『安全』兩個字即可。"
            )
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False
            }
            
            logger.info(f"發送影像至 OpenClaw 伺服器 ({self.endpoint}) 進行分析...")
            response = requests.post(self.endpoint, json=payload, timeout=10)
            # 如果 HTTP 狀態碼不是 200，會觸發異常拋出
            response.raise_for_status()
            
            # Ollama 的 JSON 回應中，回覆的內容在 'response' 欄位
            result_json = response.json()
            result_text = result_json.get("response", "").strip()
            
            logger.info(f"OpenClaw 決策結果: {result_text}")
            
            warning_msg = None
            if "安全" not in result_text or len(result_text) > 4:
                warning_msg = result_text

            return {
                "action": "forward" if not warning_msg else "caution",
                "warning": warning_msg,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"OpenClaw 連線或推理失敗: {e}")
            return {"action": "forward", "warning": None, "confidence": 0.0, "error": str(e)}
    
    def get_safe_path(self, obstacles: list) -> list:
        return []
