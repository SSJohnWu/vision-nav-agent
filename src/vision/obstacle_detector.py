"""
障礙物偵測模組
使用 OpenCV 進行物體偵測與深度分析
"""
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ObstacleDetector:
    """
    障礙物偵測器
    偵測並分類障礙物（變電箱、高低差、積水等）
    """
    
    def __init__(self):
        self.classes = ["person", "pole", "barrier", "water", "stairs", "unknown"]
        logger.info("ObstacleDetector initialized")
    
    def detect(self, frame: np.ndarray) -> list:
        """
        偵測障礙物
        
        Args:
            frame: 影像 frame
            
        Returns:
            障礙物列表
        """
        # TODO: 整合 YOLO / OpenCV DNN 模型
        # 目前為 placeholder
        
        obstacles = []
        
        # 範例：偵測大型物件（可改為 ML 模型）
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # edges = cv2.Canny(gray, 50, 150)
        
        return obstacles
    
    def classify_obstacle(self, contour) -> str:
        """分類障礙物類型"""
        # TODO: 根據形狀、大小分類
        return "unknown"
