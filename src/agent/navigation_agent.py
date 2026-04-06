"""
OpenClaw Navigation Agent
回復使用視覺多模態推理，因一般物件 (風扇、雜物) 無法單靠傳統 YOLO 辨識
"""
import logging
import time
import os
import yaml
import requests
import base64
import cv2

logger = logging.getLogger(__name__)

class NavigationAgent:
    """
    導航 Agent
    由於使用者的硬體算力瓶頸，我們改採「極限壓縮圖片 + 短時 Token 生成」的策略呼叫 Ollama
    """
    
    def __init__(self):
        self.last_api_call = 0
        self.cooldown_seconds = 3.0
        
        # 讀取 config
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                ai_config = config.get('ai', {})
                self.endpoint = ai_config.get('endpoint', 'http://127.0.0.1:11434/api/generate')
                self.model_name = ai_config.get('model', 'gemini-3-flash-preview')
        except Exception:
            self.endpoint = 'http://127.0.0.1:11434/api/generate'
            self.model_name = 'gemini-3-flash-preview'

        logger.info(f"Navigation Agent initialized. OpenClaw Endpoint: {self.endpoint}")

    def analyze_environment(self, visual_data: dict) -> dict:
        frame = visual_data.get("frame")
        if frame is None:
            return {"action": "forward", "warning": None, "confidence": 0.0}

        # 冷卻限制
        current_time = time.time()
        if (current_time - self.last_api_call) < self.cooldown_seconds:
            return {"action": "forward", "warning": None, "confidence": 0.0, "cooldown": True}
            
        self.last_api_call = current_time

        try:
            logger.info("壓縮畫面以進行高速視覺分析...")
            
            # 💡 終極加速手段 1：將畫面暴縮至 160x120。
            # 這不會影響 AI「看」出大物體（如地上的風扇），但能將神經網路卷積層的運算量降低數倍！
            small_frame = cv2.resize(frame, (160, 120))
            _, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            base64_image = base64.b64encode(buffer).decode('utf-8')

            prompt = (
                "你是一個視障者的安全導航助手。請看這張前方攝影機的低解析度即時畫面。"
                "如果有危險（如地上有風扇、電線、階梯、雜物等），請用『一句話』簡潔說明重點障礙物與建議方向。"
                "如果前方空曠安全，請只回答『安全』兩個字。"
            )
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False
            }
            
            logger.info("已將場景拋轉給 OpenClaw (Ollama) 多模態伺服器...")
            # 因為電腦老兵正在奮戰，我們設定 timeout 為 30 秒以免強行中斷，但期望它在極限壓縮下能更快回來
            response = requests.post(self.endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            result_json = response.json()
            warning_msg = result_json.get("response", "").strip()
            logger.info(f"大腦決策結果: {warning_msg}")

            # 若判斷為安全，則回傳無警告
            if "安全" in warning_msg and len(warning_msg) < 8:
                return {"action": "forward", "warning": None, "confidence": 1.0}

            return {
                "action": "caution",
                "warning": warning_msg,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"系統分析鏈斷裂: {e}")
            return {"action": "forward", "warning": None, "confidence": 0.0, "error": str(e)}
            
    def get_safe_path(self, obstacles: list) -> list:
        return []
