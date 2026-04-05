"""
語音介面模組
文字轉語音 (TTS) 與 語音辨識 (STT)
"""
import logging

logger = logging.getLogger(__name__)


class VoiceInterface:
    """
    語音介面
    負責與使用者互動的語音輸入輸出
    """
    
    def __init__(self):
        self.tts_engine = None
        self.stt_engine = None
        logger.info("VoiceInterface initialized")
    
    def speak(self, text: str):
        """
        文字轉語音輸出
        
        Args:
            text: 要說的文字
        """
        # TODO: 整合 pyttsx3 / gTTS / ElevenLabs
        logger.info(f"Speak: {text}")
        print(f"🔊 {text}")
    
    def listen(self) -> str:
        """
        聆聽語音輸入
        
        Returns:
            辨識文字
        """
        # TODO: 整合 speechRecognition
        return ""
    
    def announce_obstacle(self, obstacle_type: str, direction: str):
        """ announcement for obstacle """
        warnings = {
            "pole": "前方有電線桿，請靠左走",
            "water": "前方有積水，請繞道",
            "stairs": "前方有階梯，請小心",
            "barrier": "前方有障礙物，請減速",
        }
        msg = warnings.get(obstacle_type, f"前方有障礙物，請注意")
        self.speak(msg)
