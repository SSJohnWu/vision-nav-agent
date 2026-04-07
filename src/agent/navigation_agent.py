"""
OpenClaw Navigation Agent
混合決策大腦，整合 YOLO 極速視覺與 OpenCV 盲點雷達
"""
import logging
import time
import os
import yaml
import requests
import base64
import cv2
import sys

# 載入我們的 YOLO 混合模型技能
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.vision.obstacle_detector import ObstacleDetector

logger = logging.getLogger(__name__)

class NavigationAgent:
    """
    導航 Agent
    兼顧 0.1秒極速 與 現實環境雜物的終極保護者
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
            self.endpoint = 'http://127.0.0.1:11434/api/genesrate'
            self.model_name = 'gemini-3-flash-preview'

        logger.info(f"Navigation Agent initialized. OpenClaw Endpoint: {self.endpoint}")
        
        # 實例化我們的 YOLO + OpenCV 混合視覺技能
        self.detector = ObstacleDetector()

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
            logger.info("呼叫 YOLO-World 開放詞彙先鋒進行掃描...")
            detected_objects = self.detector.detect(frame)
            
            if len(detected_objects) == 0:
                return {"action": "forward", "warning": None, "confidence": 1.0}
            
            # 為了追求極致，我們拔除所有需要高強度算力的多模態影像推論
            # 既然 YOLO-World 已經幫我們找出所有的雜物與電風扇
            objects_str = "與".join(detected_objects)
            logger.info(f"YOLO-World 發現障礙物/雜物: {objects_str}")

            # 我們直接用 Python 字串硬幹，達成硬體極限的零延遲警告！
            warning_msg = f"請小心，前方發現{objects_str}"
            
            logger.info(f"YOLO-World 零延遲決策結果: {warning_msg}")

            return {
                "action": "caution",
                "warning": warning_msg,
                "confidence": 1.0
            }
            
        except Exception as e:
            logger.error(f"分析失敗: {e}")
            return {"action": "forward", "warning": None, "confidence": 0.0, "error": str(e)}
            
    def get_safe_path(self, obstacles: list) -> list:
        return []
