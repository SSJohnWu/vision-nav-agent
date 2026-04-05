"""
主程式入口
智慧視障輔助導航系統
"""
import sys
import logging
from agent.navigation_agent import NavigationAgent
from vision.camera_capture import CameraCapture
from audio.voice_interface import VoiceInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisionNavSystem:
    """主系統整合"""
    
    def __init__(self):
        import yaml
        import os
        
        # 讀取設定檔以獲取相機等設定
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        camera_index = 0  # 預設值
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                camera_index = config.get('camera', {}).get('index', 0)
        except Exception as e:
            logger.warning(f"無法讀取設定檔，將使用預設鏡頭: {e}")

        self.agent = NavigationAgent()
        # 允許切換不同鏡頭 (0 通常是內建，1 或 2 通常是外接鏡頭)
        self.camera = CameraCapture(camera_index=camera_index)
        self.voice = VoiceInterface()
        logger.info(f"系統初始化完成 (使用鏡頭編號: {camera_index})")
    
    def start(self):
        """啟動導航系統"""
        import time
        import cv2

        self.voice.speak("導航系統已啟動")
        logger.info("Vision Navigation System started")
        
        # 啟動相機
        try:
            self.camera.start()
        except Exception as e:
            logger.error(f"攝影機啟動失敗: {e}")
            self.voice.speak("攝影機啟動失敗，請檢查設備")
            return

        try:
            while True:
                # 1. 取出攝影機最新的一幀影像
                frame = self.camera.read_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue

                # 為了開發測試，將影像顯示在視窗上
                cv2.imshow("Vision Nav Agent (Press 'q' to exit)", frame)
                
                # 2. 將影像傳遞給 Agent 大腦做決策判斷
                # (先假裝將 frame 包進 dict，之後依據模型需求再作調整)
                visual_data = {"frame": frame}
                decision = self.agent.analyze_environment(visual_data)
                
                # 3. 根據決策判斷是否需要發用語音
                target_warning = decision.get("warning")
                if target_warning:
                    self.voice.speak(target_warning)
                
                # 聽取鍵盤指令，按下 'q' 則退出迴圈
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("使用者按下 q 鍵停止系統")
                    break
                    
        except KeyboardInterrupt:
            logger.info("使用者透過 Ctrl+C 強制終止")
        finally:
            # 安全釋放資源
            self.camera.stop()
            cv2.destroyAllWindows()
            self.voice.speak("導航系統已關閉")


if __name__ == "__main__":
    system = VisionNavSystem()
    system.start()
