"""
障礙物偵測模組
使用 Ultralytics YOLOv8n 搭配 OpenCV 邊緣掃描，達成零延遲+盲點覆蓋
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
    透過極速 YOLOv8 打擊常見物體，加上 OpenCV 掃描地面未知突起物
    """
    
    def __init__(self):
        logger.info(f"ObstacleDetector initializing YOLOv8n model...")
        
        # 退回使用最輕快的 YOLOv8 Nano 以維持 0.1 秒極速
        self.model = YOLO("yolov8n.pt")
        
        # 完整擴充 YOLOv8 的 COCO 80 種類別翻譯 (記憶體字典查詢消耗時間 < 0.0001 秒)
        self.en_to_zh_map = {
            "person": "行人", "bicycle": "腳踏車", "car": "汽車", "motorcycle": "機車", 
            "airplane": "飛機", "bus": "公車", "train": "火車", "truck": "大卡車", 
            "boat": "船隻", "traffic light": "紅綠燈", "fire hydrant": "消防栓", 
            "stop sign": "停車標誌", "parking meter": "停車收費表", "bench": "長椅", 
            "bird": "鳥類", "cat": "貓咪", "dog": "狗狗", "horse": "馬", 
            "sheep": "羊", "cow": "牛", "elephant": "大象", "bear": "熊", 
            "zebra": "斑馬", "giraffe": "長頸鹿", "backpack": "背包", 
            "umbrella": "雨傘", "handbag": "手提包", "tie": "領帶", 
            "suitcase": "行李箱", "frisbee": "飛盤", "skis": "滑雪板", 
            "snowboard": "滑雪板", "sports ball": "運動球", "kite": "風箏", 
            "baseball bat": "球棒", "baseball glove": "棒球手套", "skateboard": "滑板", 
            "surfboard": "衝浪板", "tennis racket": "網球拍", "bottle": "瓶子", 
            "wine glass": "高腳杯", "cup": "杯子", "fork": "叉子", "knife": "刀子", 
            "spoon": "湯匙", "bowl": "碗", "banana": "香蕉", "apple": "蘋果", 
            "sandwich": "三明治", "orange": "橘子", "broccoli": "花椰菜", 
            "carrot": "胡蘿蔔", "hot dog": "熱狗", "pizza": "披薩", "donut": "甜甜圈", 
            "cake": "蛋糕", "chair": "椅子", "couch": "沙發", "potted plant": "盆栽", 
            "bed": "床鋪", "dining table": "餐桌", "toilet": "馬桶", "tv": "電視", 
            "laptop": "筆電", "mouse": "滑鼠", "remote": "遙控器", "keyboard": "鍵盤", 
            "cell phone": "手機", "microwave": "微波爐", "oven": "烤箱", 
            "toaster": "烤麵包機", "sink": "水槽", "refrigerator": "冰箱", 
            "book": "書本", "clock": "時鐘", "vase": "花瓶", "scissors": "剪刀", 
            "teddy bear": "泰迪熊", "hair drier": "吹風機", "toothbrush": "牙刷"
        }
        logger.info("YOLOv8n 視覺技能與 OpenCV 底層雷達準備就緒")
    
    def detect(self, frame: np.ndarray) -> list:
        # 第一層：YOLO 極速常見物件偵測
        results = self.model(frame, conf=0.3, verbose=False)
        detected_items = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                c_id = int(box.cls[0])
                class_name = self.model.names[c_id]
                zh_name = self.en_to_zh_map.get(class_name, class_name)
                detected_items.append(zh_name)
                
        # 第二層：OpenCV 盲點突起物雷達 (專找 YOLO 沒學過的電風扇、垃圾等)
        try:
            # 將畫面轉灰階
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 只裁切畫面最下方 1/3 (也就是使用者雙腳前方即將踩到的範圍)
            h, w = gray.shape
            ROI = gray[int(h*0.66):h, :]
            
            # 使用 Canny 尋找銳利邊緣
            edges = cv2.Canny(ROI, 50, 150)
            
            # 計算雜亂邊緣的密度
            edge_pixels = np.sum(edges > 0)
            total_pixels = ROI.shape[0] * ROI.shape[1]
            edge_density = edge_pixels / total_pixels if total_pixels > 0 else 0
            
            # 如果前方的地面有超過 4% 的突起邊緣特徵，視為有雜物障礙
            if edge_density > 0.04:
                detected_items.append("地面雜物")
                logger.info(f"OpenCV 地面雷達掃描到未知的異常突起物！(密度: {edge_density:.3f})")
                
        except Exception as e:
            logger.warning(f"OpenCV 雷達異常: {e}")
                
        return list(set(detected_items))

    def classify_obstacle(self, contour) -> str:
        return "unknown"
