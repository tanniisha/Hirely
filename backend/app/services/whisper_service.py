import speech_recognition as sr
import os
from pathlib import Path

class WhisperService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def transcribe_audio(self, audio_file_path: str) -> str:

        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)

            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            raise Exception("Could not understand audio")
        except sr.RequestError as e:
            raise Exception(f"Error transcribing audio: {e}")
    
    def save_audio(self, audio_data: bytes, filename: str) -> str:

        upload_dir = Path('app/uploads/audio')
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / filename
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        
        return str(file_path)
