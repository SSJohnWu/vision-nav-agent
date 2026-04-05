"""
Vision 分析器 - 多協談整合：同時支援 WebSocket RPC + HTTP REST
自動偵測哪種方式可用，確保最高成功率
"""
import cv2
import logging
import base64
import json
import time
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

class VisionAnalyzer:
    """
    OpenClaw Vision 分析器
    自動選擇最快的可用方式：WebSocket RPC > HTTP REST
    """
    
    def __init__(self,
                 gateway_url: str = "ws://127.0.0.1:18789",
                 http_url: str = "http://127.0.0.1:18789",
                 token: str = "5243ab3a1e61c8888508216ad4683d09ac668362a05d5a7f",
                 model: str = "gemini-3-flash-preview"):
        self.gateway_url = gateway_url
        self.http_url = http_url
        self.token = token
        self.model = model
        self.ws = None
        self._ws_connected = False
        self._test_connections()
        logger.info(f"VisionAnalyzer initialized (model={model})")
    
    def _test_connections(self):
        """測試兩種連線方式，找出可用的"""
        # 先測 HTTP REST（簡單快速）
        try:
            import requests
            resp = requests.get(
                f"{self.http_url}/v1/models",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            if resp.status_code == 200:
                logger.info("HTTP REST: /v1/models accessible")
                self._method = "http"
                return
        except Exception as e:
            logger.warning(f"HTTP REST test failed: {e}")
        
        # 測 WebSocket RPC
        try:
            import websocket
            ws = websocket.WebSocket()
            ws.settimeout(5)
            ws.connect(self.gateway_url)
            
            # 等待 challenge
            challenge_raw = ws.recv()
            challenge = json.loads(challenge_raw)
            nonce = challenge['payload']['nonce']
            
            # 發送 connect
            connect_req = {
                "type": "req", "id": "c1", "method": "connect",
                "params": {
                    "minProtocol": 3, "maxProtocol": 3,
                    "client": {"id": "vision", "version": "1.0", "platform": "windows", "mode": "operator"},
                    "role": "operator",
                    "scopes": ["operator.read", "operator.write"],
                    "caps": [], "commands": [], "permissions": {},
                    "auth": {"token": self.token},
                    "locale": "zh-TW",
                    "userAgent": "vision-nav/1.0"
                }
            }
            ws.send(json.dumps(connect_req))
            hello = ws.recv()
            
            self.ws = ws
            self._ws_connected = True
            self._method = "websocket"
            logger.info("WebSocket RPC: connected successfully")
            return
        except Exception as e:
            logger.warning(f"WebSocket test failed: {e}")
        
        self._method = None
        logger.error("All connection methods failed")
    
    def analyze_frame(self, frame: np.ndarray,
                     prompt: str = "請描述這張圖片中的導航障礙物與路徑建議。") -> Optional[str]:
        """分析圖片，速度最快的方式"""
        if frame is None:
            return None
        
        # 將 OpenCV 影像轉為 Base64
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        b64_image = base64.b64encode(buffer).decode('utf-8')
        
        if self._method == "http":
            return self._analyze_http(b64_image, prompt)
        elif self._method == "websocket":
            return self._analyze_ws(b64_image, prompt)
        else:
            logger.error("No working connection method")
            return None
    
    def _analyze_http(self, b64_image: str, prompt: str) -> Optional[str]:
        """HTTP REST 方式（可能需要調整格式）"""
        import requests
        
        payload = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }],
            "stream": False
        }
        
        try:
            resp = requests.post(
                f"{self.http_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=20
            )
            logger.info(f"HTTP Response: {resp.status_code} — {resp.text[:300]}")
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"HTTP analysis failed: {e}")
            return None
    
    def _analyze_ws(self, b64_image: str, prompt: str) -> Optional[str]:
        """WebSocket RPC 方式（原生協定，成功率最高）"""
        import websocket
        
        try:
            if not self._ws_connected or self.ws is None:
                self._test_connections()
            
            req_id = f"v-{int(time.time()*1000)}"
            msg = {
                "type": "req", "id": req_id,
                "method": "chat.send",
                "params": {
                    "prompt": prompt,
                    "model": self.model,
                    "imageBase64": b64_image,
                    "imageMediaType": "image/jpeg"
                }
            }
            
            self.ws.send(json.dumps(msg))
            
            # 等回應（最多 20 秒）
            deadline = time.time() + 20
            while time.time() < deadline:
                raw = self.ws.recv()
                data = json.loads(raw)
                
                if data.get("id") == req_id:
                    if data.get("ok"):
                        return data.get("payload", {}).get("content", str(data))
                    else:
                        logger.error(f"WS RPC error: {data.get('error')}")
                        return None
                
                # session.message 事件（streaming 回應）
                if data.get("type") == "event" and "session.message" in data.get("event", ""):
                    content = data.get("payload", {}).get("content", "")
                    if content:
                        return content
            
            logger.warning("WS analysis timed out")
            return None
            
        except Exception as e:
            logger.error(f"WS analysis failed: {e}")
            self._ws_connected = False
            return None
    
    def close(self):
        if self.ws:
            try: self.ws.close()
            except: pass
            self.ws = None
            self._ws_connected = False
    
    def __del__(self):
        self.close()


# --- 測試 ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    
    print("=" * 50)
    print("VisionAnalyzer 測試（自動偵測可用方式）")
    print("=" * 50)
    
    analyzer = VisionAnalyzer()
    print(f"使用的連線方式: {analyzer._method}")
    
    # 測攝影機
    try:
        from camera_capture import CameraCapture
        cam = CameraCapture(0)
        cam.start()
        frame = cam.read_frame()
        
        if frame is not None:
            print(f"📷 影像已擷取 (shape: {frame.shape})")
            print("🔍 分析中...\n")
            
            result = analyzer.analyze_frame(
                frame,
                prompt="請描述這張圖片中的導航障礙物與路徑建議。"
            )
            
            print(f"✅ 分析結果:\n{result}")
        else:
            print("❌ 無法擷取影像")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        analyzer.close()
