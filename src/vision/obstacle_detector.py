"""
障礙物偵測模組
使用 Ultralytics YOLOv8 進行高速物體偵測技能，作為 OpenClaw 大腦的前置作業
"""
import cv2
import numpy as np
import logging
import os
import yaml
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class ObstacleDetector:
    """
    障礙物偵測先鋒技能
    負責極速掃描常見障礙物，並輸出中文化標籤
    """
    
    def __init__(self):
        # 讀取 config
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                ai_config = config.get('obstacle_detection', {})
                self.model_name = ai_config.get('model', 'yolov8n.pt')
        except Exception:
            self.model_name = 'yolov8n.pt'
        
        logger.info(f"ObstacleDetector initializing YOLO model ({self.model_name})... (剛開始可能會連線下載)")
        # 首次載入會從網路下載權重
        self.model = YOLO(self.model_name)
        
        # 簡易翻譯字典 (COCO Dataset 常見障礙物對照表)
        self.en_to_zh_map = {
            "person": "行人",
            "car": "汽車",
            "motorcycle": "機車",
            "bus": "公車",
            "truck": "大卡車",
            "bicycle": "腳踏車",
            "traffic light": "紅綠燈",
            "stop sign": "標誌牌",
            "bench": "長椅",
            "chair": "椅子",
            "potted plant": "盆栽",
            "fire hydrant": "消防栓",
            "dog": "牽繩狗狗",
            "cat": "貓咪"
        }
        logger.info("YOLOv8 視覺技能準備就緒")
    
    def detect(self, frame: np.ndarray) -> list:
        """
        偵測障礙物
        傳回在這張畫面中找到的所有具體物件名稱 (去除重複)
        """
        # conf=0.4 表示信心度超過 40% 才抓，避免一點黑影就鬼叫
        results = self.model(frame, conf=0.4, verbose=False)
        
        detected_items = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # 取得類別 ID 轉為字串
                c_id = int(box.cls[0])
                class_name = self.model.names[c_id]
                # 將英文字串轉成白話中文
                zh_name = self.en_to_zh_map.get(class_name, class_name)
                detected_items.append(zh_name)
                
        # 確保回傳不會一連串「行人、行人、行人」，用 Set 濾掉重複項
        return list(set(detected_items))

    def classify_obstacle(self, contour) -> str:
        return "unknown"
