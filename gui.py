import customtkinter as ctk
from PIL import ImageGrab
import tkinter as tk
import keyboard
import datetime
import pyperclip

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
        
        self.withdraw()
        self.attributes("-fullscreen", False)
        
        if x2 - x1 > 10 and y2 - y1 > 10:
            image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.callback(image)
        
        self.destroy()

class InterviewAssistantGUI(ctk.CTk):
    def __init__(self, ai_service, audio_service_factory):
        super().__init__()
        print("GUI: Super init done")
        self.ai_service = ai_service
        
        # Initialize Audio Service with callbacks
        print("GUI: Initializing Audio Service")
        self.audio_service = audio_service_factory(self.on_audio_text, self.on_audio_status)
        
        # Custom Context Data
        self.cv_text = ""
        self.job_text = ""

        self.personas = {
            "Personalizado (CV + Job)": "DYNAMIC_MODE",
            "Asistente General (Otros)": "Eres un asistente de inteligencia artificial útil, preciso y profesional. Responde de manera clara y concisa a cualquier pregunta o tarea que se te plantee."
        }

        self._init_window()
        self._init_ui()
        self._init_bindings()
        
        # Session Logging
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"session_{timestamp}.txt"
        self.history = []
        self.is_collapsed = False

    def _init_window(self):
        self.title("Interview Copilot")
        self.geometry("500x600+100+100")
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.configure(fg_color="#1a1a1a")
        self.attributes("-alpha", 0.90)

    def _init_ui(self):
        # Main Container with padding
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # --- Top Bar: Title & Window Controls ---
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=30)
        self.top_bar.pack(fill="x", pady=(0, 10))
        
        self.title_label = ctk.CTkLabel(self.top_bar, text="Interview Assistant", font=("Roboto Medium", 16), text_color="#e5e7eb")
        self.title_label.pack(side="left")

        # Window Controls (Right aligned)
        self.close_btn = ctk.CTkButton(self.top_bar, text="✕", width=25, height=25, command=self.destroy, 
                                       fg_color="#ef4444", hover_color="#dc2626", corner_radius=6)
        self.close_btn.pack(side="right", padx=(5, 0))
        
        self.collapse_btn = ctk.CTkButton(self.top_bar, text="−", width=25, height=25, command=self.toggle_collapse, 
                                          fg_color="#4b5563", hover_color="#374151", corner_radius=6)
        self.collapse_btn.pack(side="right")

        # --- Settings Area ---
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="#262626", corner_radius=8)
        self.settings_frame.pack(fill="x", pady=(0, 10))
        
        # Persona Selector
        self.persona_var = ctk.StringVar(value="Personalizado (CV + Job)")
        self.persona_menu = ctk.CTkOptionMenu(self.settings_frame, values=list(self.personas.keys()), 
                                              variable=self.persona_var, height=30,
                                              fg_color="#374151", button_color="#1f2937",
                                              font=("Arial", 11))
        self.persona_menu.pack(fill="x", padx=10, pady=(10, 5))

        # Edit Context Button
        self.context_btn = ctk.CTkButton(self.settings_frame, text="📝 Cargar CV y Búsqueda", 
                                         command=self.open_context_window,
                                         fg_color="#2563eb", hover_color="#1d4ed8", height=25, font=("Arial", 11))
        self.context_btn.pack(fill="x", padx=10, pady=(0, 10))

        # Audio Device Selector
        mic_names = self.audio_service.get_devices()
        self.mic_options = [f"{i}: {name}" for i, name in enumerate(mic_names)] if mic_names else ["Default"]
        self.mic_var = ctk.StringVar(value=self.mic_options[0])
        self.mic_menu = ctk.CTkOptionMenu(self.settings_frame, values=self.mic_options, 
                                          variable=self.mic_var, height=25,
                                          command=self.change_mic, font=("Arial", 10),
                                          fg_color="#374151", button_color="#1f2937")
        self.mic_menu.pack(fill="x", padx=10, pady=(0, 10))

        # --- Action Bar ---
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=(0, 10))

        # Start/Stop Button (Big & Prominent)
        self.status_btn = ctk.CTkButton(self.action_frame, text="▶️ INICIAR ESCUCHA", height=40, 
                                        command=self.audio_service.toggle_listening, 
                                        fg_color="#10b981", hover_color="#059669",
                                        font=("Roboto Medium", 14))
        self.status_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Snapshot Button
        self.snap_btn = ctk.CTkButton(self.action_frame, text="📷", width=40, height=40, 
                                      command=self.start_snipping, 
                                      fg_color="#eab308", hover_color="#ca8a04")
        self.snap_btn.pack(side="right")

        # --- Content Area ---
        
        # Transcript (Subtle)
        self.transcript_label = ctk.CTkLabel(self.main_frame, text="Esperando audio...", 
                                             wraplength=460, justify="left", 
                                             font=("Arial Italic", 12), text_color="#9ca3af")
        self.transcript_label.pack(fill="x", pady=(0, 5))

        # Answer Box (Main Focus)
        self.answer_box = ctk.CTkTextbox(self.main_frame, font=("Consolas", 14), 
                                         text_color="#4ade80", fg_color="#1f2937", 
                                         wrap="word", corner_radius=8, border_width=1, border_color="#374151")
        self.answer_box.pack(fill="both", expand=True, pady=(0, 10))
        self.answer_box.configure(state="disabled")

        # --- Footer Controls ---
        self.footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=30)
        self.footer_frame.pack(fill="x")

        # Opacity Slider
        self.slider_label = ctk.CTkLabel(self.footer_frame, text="Opacidad:", font=("Arial", 10), text_color="#6b7280")
        self.slider_label.pack(side="left", padx=(0, 5))
        
        self.slider = ctk.CTkSlider(self.footer_frame, from_=0.2, to=1.0, number_of_steps=20, 
                                    command=self.change_opacity, width=100, progress_color="#10b981")
        self.slider.set(0.90)
        self.slider.pack(side="left", pady=5)

        # Refine Buttons
        self.minus_btn = ctk.CTkButton(self.footer_frame, text="Resumir", width=60, height=25, 
                                       command=lambda: self.refine_answer("short"), 
                                       fg_color="#4b5563", font=("Arial", 11))
        self.minus_btn.pack(side="left", padx=(15, 5))
        
        self.plus_btn = ctk.CTkButton(self.footer_frame, text="Expandir", width=60, height=25, 
                                      command=lambda: self.refine_answer("long"), 
                                      fg_color="#4b5563", font=("Arial", 11))
        self.plus_btn.pack(side="left", padx=5)

        # Copy Button
        self.copy_btn = ctk.CTkButton(self.footer_frame, text="📋 Copiar", width=70, height=25, 
                                      command=self.copy_answer, 
                                      fg_color="#374151", hover_color="#4b5563", font=("Arial", 11))
        self.copy_btn.pack(side="right")

    def _init_bindings(self):
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
        keyboard.add_hotkey('F8', self.audio_service.toggle_listening)
        keyboard.add_hotkey('f9', self.toggle_panic_mode)
        self.is_panic = False

    # --- Logic ---

    def on_audio_status(self, is_listening):
        if is_listening:
            self.status_btn.configure(text="⏹️ DETENER ESCUCHA", fg_color="#ef4444", hover_color="#dc2626")
        else:
            self.status_btn.configure(text="▶️ INICIAR ESCUCHA", fg_color="#10b981", hover_color="#059669")

    def on_audio_text(self, text):
        self.transcript_label.configure(text=f"🗣️: {text}")
        self.generate_answer(text)

    def change_mic(self, choice):
        if ":" in choice:
            index = int(choice.split(":")[0])
            if self.audio_service.set_device(index):
                self.transcript_label.configure(text=f"🎤 Mic cambiado a: {choice}")

    def open_context_window(self):
        window = ctk.CTkToplevel(self)
        window.title("Configurar Contexto")
        window.geometry("600x500")
        window.attributes("-topmost", True)
        
        # CV Section
        ctk.CTkLabel(window, text="Tu CV (Copia y pega el texto):", font=("Arial", 12, "bold")).pack(pady=(10, 5), padx=10, anchor="w")
        cv_box = ctk.CTkTextbox(window, height=150)
        cv_box.pack(fill="x", padx=10)
        cv_box.insert("0.0", self.cv_text)
        
        # Job Description Section
        ctk.CTkLabel(window, text="Descripción del Puesto (Busqueda):", font=("Arial", 12, "bold")).pack(pady=(10, 5), padx=10, anchor="w")
        job_box = ctk.CTkTextbox(window, height=150)
        job_box.pack(fill="x", padx=10)
        job_box.insert("0.0", self.job_text)
        
        def save_context():
            self.cv_text = cv_box.get("0.0", "end").strip()
            self.job_text = job_box.get("0.0", "end").strip()
            window.destroy()
            
        ctk.CTkButton(window, text="Guardar Contexto", command=save_context, fg_color="#10b981", hover_color="#059669").pack(pady=20)

    def generate_answer(self, question, image=None):
        self.answer_box.configure(state="normal")
        self.answer_box.delete("0.0", "end")
        self.answer_box.insert("0.0", "💭 Pensando...")
        self.answer_box.configure(state="disabled")

        # Context
        context_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in self.history[-3:]])
        
        selected_persona = self.persona_var.get()
        if selected_persona == "Personalizado (CV + Job)":
            if not self.cv_text and not self.job_text:
                persona_role = "ACTÚA COMO: Candidato en entrevista. (ADVERTENCIA: No has cargado CV ni Descripción del puesto. Usa el botón 'Cargar CV y Búsqueda' para mejorar las respuestas)."
            else:
                persona_role = f"""
                ACTÚA COMO: El candidato descrito en el siguiente CV.
                CONTEXTO: Estás en una entrevista para el puesto descrito en la BÚSQUEDA.
                
                --- TU CV ---
                {self.cv_text}
                
                --- BÚSQUEDA / PUESTO ---
                {self.job_text}
                
                INSTRUCCIONES:
                - Responde las preguntas basándote ESTRICTAMENTE en la experiencia del CV.
                - Si te preguntan algo que no está en el CV pero es requerido en la Búsqueda, intenta relacionarlo con tu experiencia previa o sé honesto pero proactivo.
                - Mantén un tono profesional y seguro.
                """
        else:
            persona_role = self.personas.get(selected_persona, self.personas["Asistente General (Otros)"])
        
        prompt = f"""
        {persona_role}
        Historial reciente:
        {context_str}
        
        Entrada actual: {question}
        
        Instrucción: Si hay imagen, extrae el código/texto y resuélvelo. Si es texto, responde breve, directo y técnico.
        """

        # Run in thread to not block UI
        import threading
        def _run_ai():
            answer = self.ai_service.generate_response(prompt, image)
            self.after(0, lambda: self.update_answer(question, answer))
        
        threading.Thread(target=_run_ai, daemon=True).start()

    def update_answer(self, question, answer):
        self.answer_box.configure(state="normal")
        self.answer_box.delete("0.0", "end")
        self.answer_box.insert("0.0", answer)
        self.answer_box.configure(state="disabled")
        
        self.history.append((question, answer))
        
        # Auto pause
        self.audio_service.stop_listening()

    def refine_answer(self, mode):
        if not self.history: return
        prompt = "Resume la respuesta anterior." if mode == "short" else "Explica con más detalle."
        self.generate_answer(prompt)

    def start_snipping(self):
        self.attributes("-alpha", 0)
        ScreenSnipper(self, self.finish_snipping)

    def finish_snipping(self, image):
        self.attributes("-alpha", self.slider.get())
        self.transcript_label.configure(text="📸 Analyzing image...")
        self.generate_answer("Analiza esta imagen.", image=image)

    # --- Window Utils ---
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

    def change_opacity(self, value):
        self.attributes("-alpha", value)

    def toggle_panic_mode(self):
        if self.is_panic:
            self.deiconify()
            self.is_panic = False
        else:
            self.withdraw()
            self.is_panic = True

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.geometry("500x130")
            self.collapse_btn.configure(text="+")
            self.settings_frame.pack_forget()
            self.transcript_label.pack_forget()
            self.answer_box.pack_forget()
            self.footer_frame.pack_forget()
        else:
            self.geometry("500x600")
            self.collapse_btn.configure(text="−")
            self.settings_frame.pack(fill="x", pady=(0, 10), after=self.top_bar)
            self.action_frame.pack(fill="x", pady=(0, 10), after=self.settings_frame)
            self.transcript_label.pack(fill="x", pady=(0, 5), after=self.action_frame)
            self.answer_box.pack(fill="both", expand=True, pady=(0, 10), after=self.transcript_label)
            self.footer_frame.pack(fill="x", after=self.answer_box)

    def copy_answer(self):
        try:
            text = self.answer_box.get("0.0", "end").strip()
            if text:
                pyperclip.copy(text)
                self.copy_btn.configure(text="✅")
                self.after(1000, lambda: self.copy_btn.configure(text="📋 Copy"))
        except: pass
