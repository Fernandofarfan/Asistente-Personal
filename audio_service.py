import speech_recognition as sr
import threading
import time
import os
from datetime import datetime

class AudioService:
    def __init__(self, on_text_callback, on_status_callback):
        self.recognizer = sr.Recognizer()
        # CRITICAL SETTINGS FOR VB-CABLE / SYSTEM AUDIO
        self.recognizer.energy_threshold = 300  # Fixed low threshold
        self.recognizer.dynamic_energy_threshold = False # Do not auto-adjust
        
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.on_text_callback = on_text_callback
        self.on_status_callback = on_status_callback
        self.listen_thread = None
        self.log_file = "audio_debug.log"
        
        # Clear log
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"AudioService initialized at {datetime.now()}\n")
        except:
            pass

    def log(self, message):
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass

    def get_devices(self):
        try:
            return sr.Microphone.list_microphone_names()
        except:
            return []

    def set_device(self, index):
        self.log(f"Setting device to index {index}")
        try:
            self.microphone = sr.Microphone(device_index=index)
            # Re-enforce settings in case they were reset
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = False
            self.log("Device set. Threshold=300, Dynamic=False")
            return True
        except Exception as e:
            self.log(f"Error setting device: {e}")
            return False

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            self.on_status_callback(True)
            self.log("Started listening")

    def stop_listening(self):
        self.is_listening = False
        self.on_status_callback(False)
        self.log("Stopped listening")

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def _listen_loop(self):
        self.log("Entering listen loop")
        while self.is_listening:
            try:
                with self.microphone as source:
                    try:
                        # Listen for audio
                        # Increased phrase_time_limit to capture longer sentences
                        # self.log("Listening for phrase...") # Too verbose for loop
                        audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=15)
                        self.log("Audio captured, recognizing...")
                        
                        # Transcribe
                        text = self.recognizer.recognize_google(audio, language="es-ES")
                        self.log(f"Recognized: {text}")
                        if text:
                            self.on_text_callback(text)
                        
                    except sr.WaitTimeoutError:
                        # This is normal if no speech is detected in 'timeout' seconds
                        continue
                    except sr.UnknownValueError:
                        # self.log("UnknownValueError (Speech unintelligible)")
                        pass
                    except Exception as e:
                        self.log(f"Error Recog: {e}")
            except Exception as e:
                self.log(f"Mic Error: {e}")
                time.sleep(1)
