import threading
import time
import tkinter as tk
import customtkinter as ctk
import speech_recognition as sr
import google.generativeai as genai
import keyboard
import sys

from PIL import Image, ImageGrab, ImageTk
import pyperclip
import os
import time
import datetime
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    model = None

class ScreenSnipper(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.3)
        self.attributes("-topmost", True)
        self.configure(fg_color="black")
        self.overrideredirect(True)
        
        self.canvas = ctk.CTkCanvas(self, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        
        self.withdraw() # Hide immediately
        self.attributes("-fullscreen", False) # Release fullscreen reference
        
        if x2 - x1 > 10 and y2 - y1 > 10:
            # Capture
            image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.callback(image)
        
        self.destroy()

class InterviewAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Persona Definitions
        self.personas = {
            "SysAdmin": "Sos un experto SysAdmin en una entrevista técnica.",
            "Python Dev": "Sos un experto desarrollador Python Senior.",
            "Java Dev": "Sos un experto desarrollador Java Senior.",
            "DevOps": "Sos un experto ingeniero DevOps (Docker, K8s, CI/CD).",
            "HR Interview": "Sos un experto en recursos humanos ayudando con respuestas conductuales (STAR)."
        }

        # Window Setup
        self.title("Interview Copilot")
        self.geometry("600x200+100+100")
        self.attributes("-topmost", True)  # Always on top
        self.overrideredirect(True)       # Remove window borders
        self.configure(fg_color="#1a1a1a") # Dark background
        self.attributes("-alpha", 0.85)    # Semi-transparent

        # Dragging functionality
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

        # UI Elements
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=30)
        self.header_frame.pack(fill="x", pady=(0, 5))

        # Persona Selector
        self.persona_var = ctk.StringVar(value="SysAdmin")
        self.persona_menu = ctk.CTkOptionMenu(self.header_frame, values=list(self.personas.keys()), 
                                              variable=self.persona_var, width=120, height=25)
        self.persona_menu.pack(side="left")

        # Snapshot Button
        self.snap_btn = ctk.CTkButton(self.header_frame, text="📷", width=30, height=25, command=self.start_snipping, fg_color="#eab308")
        self.snap_btn.pack(side="left", padx=(5,0))

        # Status Label
        self.status_label = ctk.CTkLabel(self.header_frame, text="⏸️ Paused (F8)", text_color="gray", width=90)
        self.status_label.pack(side="left", padx=5)

        # Latency Label
        self.latency_label = ctk.CTkLabel(self.header_frame, text="📶 0ms", text_color="gray", width=60)
        self.latency_label.pack(side="left", padx=5)

        # Panic Mode Hotkey
        keyboard.add_hotkey('f9', self.toggle_panic_mode)
        self.is_panic = False

        # Session Logging
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"session_{timestamp}.txt"
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"Interview Log - {timestamp}\n----------------------------\n")

        self.history = []  # Store conversation history
        self.is_collapsed = False

        self.transcript_label = ctk.CTkLabel(self.main_frame, text="Waiting for audio...", wraplength=580, justify="left", font=("Arial", 12))
        self.transcript_label.pack(fill="x", pady=(5, 0))

        # Scrollable Answer Box (Replaces Label) - Fixed Colors for Dark Mode
        self.answer_box = ctk.CTkTextbox(self.main_frame, height=150, font=("Consolas", 14), 
                                         text_color="#4ade80", fg_color="#1f2937", wrap="word")
        self.answer_box.pack(fill="both", expand=True, pady=(10, 0))
        self.answer_box.configure(state="disabled") # Read-only initially
        
        # Chat Input (Hidden by default)
        self.chat_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.chat_entry = ctk.CTkEntry(self.chat_frame, placeholder_text="Type generic question...")
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.chat_entry.bind("<Return>", lambda e: self.send_chat())
        self.chat_send_btn = ctk.CTkButton(self.chat_frame, text="➤", width=30, command=self.send_chat)
        self.chat_send_btn.pack(side="right")
        
        # Footer Frame
        self.footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=30)
        self.footer_frame.pack(fill="x", pady=(5, 0))
        
        # Transparency Slider
        self.slider = ctk.CTkSlider(self.footer_frame, from_=0.1, to=1.0, number_of_steps=20, command=self.change_opacity, width=100)
        self.slider.set(0.85)
        self.slider.pack(side="left", pady=5)
        
        # Refinement Buttons
        self.minus_btn = ctk.CTkButton(self.footer_frame, text="➖", width=30, height=25, command=lambda: self.refine_answer("short"), fg_color="#4b5563")
        self.minus_btn.pack(side="left", padx=(10, 2))
        self.plus_btn = ctk.CTkButton(self.footer_frame, text="➕", width=30, height=25, command=lambda: self.refine_answer("long"), fg_color="#4b5563")
        self.plus_btn.pack(side="left", padx=2)

        # Chat Toggle Button
        self.chat_btn = ctk.CTkButton(self.footer_frame, text="⌨️", width=30, height=25, command=self.toggle_chat, fg_color="#374151")
        self.chat_btn.pack(side="left", padx=5)

        # Copy Button
        self.copy_btn = ctk.CTkButton(self.footer_frame, text="📋 Copy", width=60, height=25, command=self.copy_answer, fg_color="#374151")
        self.copy_btn.pack(side="right")

        # Close Button
        self.close_btn = ctk.CTkButton(self.main_frame, text="X", width=30, height=30, command=self.close_app, fg_color="red")
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Collapse Button
        self.collapse_btn = ctk.CTkButton(self.main_frame, text="🔽", width=30, height=30, command=self.toggle_collapse, fg_color="#4b5563")
        self.collapse_btn.place(relx=0.92, rely=0.0, anchor="ne")

        # Clear Context Button
        self.clear_btn = ctk.CTkButton(self.main_frame, text="🗑️", width=30, height=30, command=self.clear_context, fg_color="#4b5563")
        self.clear_btn.place(relx=0.84, rely=0.0, anchor="ne")

        # Logic Variables
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise once
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        # Start background threads
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()
        
        # Hotkey
        keyboard.add_hotkey('F8', self.toggle_listening)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def close_app(self):
        self.destroy()
        sys.exit()

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        status = "🔴 LISTENING..." if self.is_listening else "⏸️ Paused"
        color = "#ef4444" if self.is_listening else "gray"
        self.status_label.configure(text=status, text_color=color)

    def clear_context(self):
        self.history = []
        self.answer_label.configure(text="🧹 Context cleared")
        self.update_transcript("Context reset.")

    def copy_answer(self):
        try:
            text = self.answer_box.get("0.0", "end").strip()
            if text:
                pyperclip.copy(text)
                self.copy_btn.configure(text="✅ Copied!")
                self.after(2000, lambda: self.copy_btn.configure(text="📋 Copy"))
        except:
            pass

    def toggle_panic_mode(self):
        if self.is_panic:
            self.deiconify() # Restore
            self.is_panic = False
        else:
            self.withdraw() # Instant hide
            self.is_panic = True

    def change_opacity(self, value):
        self.attributes("-alpha", value)

    def toggle_chat(self):
        if self.chat_frame.winfo_ismapped():
            self.chat_frame.pack_forget()
        else:
            self.chat_frame.pack(fill="x", pady=(5, 0), after=self.answer_box)
            self.chat_entry.focus()

    def send_chat(self):
        text = self.chat_entry.get()
        if text:
            self.update_transcript(f"⌨️ You: {text}")
            self.generate_answer(text)
            self.chat_entry.delete(0, 'end')

    def refine_answer(self, mode):
        if not self.history:
            return
            
        prompt = ""
        if mode == "short":
            prompt = "Resume la respuesta anterior para que sea MUY breve y directa."
        elif mode == "long":
            prompt = "Explica la respuesta anterior con más detalle técnico y ejemplos."
            
        self.update_transcript(f"🔄 Refine ({mode})...")
        self.generate_answer(prompt)

    def start_snipping(self):
        self.attributes("-alpha", 0) # Hide main window
        ScreenSnipper(self, self.finish_snipping)

    def finish_snipping(self, image):
        self.attributes("-alpha", self.slider.get()) # Restore opacity
        self.update_transcript("📸 Image captured! Analyzing...")
        self.generate_answer("Analiza esta imagen (captura de pantalla) y dame la solución o respuesta técnica.", image=image)

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.geometry("600x60")
            self.collapse_btn.configure(text="🔼")
            # Hide unnecessary elements
            self.transcript_label.pack_forget()
            self.answer_box.pack_forget()
            self.footer_frame.pack_forget()
        else:
            self.geometry("600x400") # Increased height for textbox
            self.collapse_btn.configure(text="🔽")
            # Show elements
            self.transcript_label.pack(fill="x", pady=(5, 0))
            self.answer_box.pack(fill="both", expand=True, pady=(10, 0))
            self.footer_frame.pack(fill="x", pady=(5, 0))
            
            # Revisit chat toggle state if it was open... simplified for now
            if self.chat_frame.winfo_ismapped():
                self.chat_frame.pack_forget() # Reset chat toggle on expand for simplicity

    def listen_loop(self):
        while True:
            if self.is_listening:
                try:
                    with self.microphone as source:
                        # self.update_transcript("👂 Escuchando...")
                        try:
                            # Listen for audio
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                            
                            self.update_transcript("⏳ Procesando voz...")
                            
                            # Transcribe
                            text = self.recognizer.recognize_google(audio, language="es-ES")
                            self.update_transcript(f"🗣️: {text}")
                            
                            # Generate Answer
                            self.generate_answer(text)
                            
                        except sr.WaitTimeoutError:
                            # self.update_transcript("... (Silencio)")
                            continue
                        except sr.UnknownValueError:
                            self.update_transcript("❌ No entendí el audio")
                            pass
                        except Exception as e:
                            self.update_transcript(f"Error Recog: {e}")
                            print(f"Error: {e}")
                except Exception as e:
                    self.update_transcript(f"Error Mic: {e}")
                    print(f"Mic Error: {e}")
                    time.sleep(1)
            else:
                time.sleep(0.1)

    def update_transcript(self, text):
        self.transcript_label.configure(text=text)

    def generate_answer(self, question, image=None):
        if not model:
            self.update_answer("⚠️ API Key missing")
            return

        self.update_answer("💭 Thinking...")
        
        # Build context from history
        context_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in self.history[-3:]]) # Keep last 3 turns
        
        # Get persona prompt
        persona_role = self.personas.get(self.persona_var.get(), self.personas["SysAdmin"])
        
        prompt_text = f"""
        {persona_role}
        Historial reciente:
        {context_str}
        
        Entrada actual: {question}
        
        Instrucción: Si hay imagen, extrae el código/texto y resuélvelo. Si es texto, responde breve, directo y técnico.
        """
        
        try:
            # Add safety settings to avoid blocking
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            content_input = [prompt_text]
            if image:
                content_input.append(image)
            
            start_time = time.time()
            response = model.generate_content(content_input, safety_settings=safety_settings)
            latency = time.time() - start_time
            
            # Update Latency Indicator
            color = "#4ade80" # Green
            if latency > 2: color = "#facc15" # Yellow
            if latency > 5: color = "#ef4444" # Red
            self.latency_label.configure(text=f"📶 {latency:.1f}s", text_color=color)
            
            # Try to get text from candidates first (more reliable)
            answer = None
            if response.candidates and len(response.candidates) > 0:
                if response.candidates[0].content.parts:
                    answer = response.candidates[0].content.parts[0].text
            
            # Fallback to response.text
            if not answer and response.text:
                answer = response.text
                
            if answer:
                self.update_answer(answer.strip())
                # Auto-pause after showing answer to give time to read
                time.sleep(1)  # Small delay before pausing
                self.is_listening = False
                self.status_label.configure(text="⏸️ Paused (Press F8 to continue)", text_color="gray")
                
                # Update history
                self.history.append((question, answer.strip()))
            else:
                self.update_answer("⚠️ No answer generated (empty response)")
                
        except Exception as e:
            self.update_answer(f"AI Error: {str(e)[:100]}")

    def update_answer(self, text):
        self.answer_box.configure(state="normal")
        self.answer_box.delete("0.0", "end")
        self.answer_box.insert("0.0", text)
        self.answer_box.configure(state="disabled")
        
        # Log to file
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] A: {text}\n")
                f.write("-" * 20 + "\n")
        except:
            pass

import logging
import traceback

# Setup logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    try:
        app = InterviewAssistant()
        app.mainloop()
    except Exception as e:
        logging.critical("App crashed!", exc_info=True)
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("App crashed! Check error_log.txt")
