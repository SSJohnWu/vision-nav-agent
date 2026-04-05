"""
影像擷取模組
使用 OpenCV 進行攝影機輸入
"""
import cv2
import logging
import numpy as np

logger = logging.getLogger(__name__)


class CameraCapture:
    """攝影機擷取"""
    
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        logger.info(f"CameraCapture initialized (index={camera_index})")
    
    def start(self):
        """啟動攝影機"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error("無法開啟攝影機")
            raise RuntimeError("Camera not available")
        logger.info("攝影機已啟動")
    
    def read_frame(self) -> np.ndarray:
        """讀取一幀"""
        if self.cap is None:
            self.start()
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("無法讀取影像")
            return None
        return frame
    
    def stop(self):
        """關閉攝影機"""
        if self.cap:
            self.cap.release()
            logger.info("攝影機已關閉")
