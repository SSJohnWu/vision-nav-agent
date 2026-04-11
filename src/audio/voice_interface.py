"""
語音介面模組
文字轉語音 (TTS) 與 語音辨識 (STT)
"""
import logging
import speech_recognition as sr
import sounddevice as sd
import numpy as np

logger = logging.getLogger(__name__)


class VoiceInterface:
    """
    語音介面
    負責與使用者互動的語音輸入輸出
    """
    
    def __init__(self):
        self.tts_engine = None
        self.stt_engine = sr.Recognizer()
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
        try:
            logger.info("請開始說話...")
            print("🎤 請語音輸入 (自動錄音 5 秒)...")
            
            fs = 16000
            duration = 5
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            
            # 轉換格式給 speech_recognition
            audio = sr.AudioData(recording.tobytes(), fs, 2)
            
            logger.info("語音辨識中...")
            text = self.stt_engine.recognize_google(audio, language='zh-TW')
            logger.info(f"辨識結果: {text}")
            print(f"👂 聽到: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("無法辨識語音內容")
            return ""
        except sr.RequestError as e:
            logger.error(f"語音識別服務異常: {e}")
            return ""
        except Exception as e:
            logger.error(f"語音擷取發生錯誤: {e}")
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
