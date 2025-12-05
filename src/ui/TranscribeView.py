import os
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backend import AudioHandler
from backend import Transcriber
from utils import utils

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TranscribeView(ctk.CTkFrame):
    """
    Gestisce la logica di caricamento audio, ritaglio, visualizzazione waveform
    e interazione con il backend di trascrizione.
    """

    def __init__(self, master, on_complete_callback=None):
        super().__init__(master)

        # Callback per avvisare la main app quando la trascrizione finisce
        self.on_complete_callback = on_complete_callback

        # Inizializzazione Logica
        self.audio_handler = AudioHandler.AudioHandler()
        self.transcriber = Transcriber.Transcriber()
        utils.setup_ffmpeg()  # Setup una tantum

        self.create_ui()

    def create_ui(self):
        # Header
        ctk.CTkLabel(self, text="Ultimate Sbobinator Turbo Deluxe 5000", font=("Arial", 24, "bold")).pack(pady=10)

        # Input Frame
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.pack(pady=10, padx=10, fill="x")

        self.btn_file = ctk.CTkButton(self.frame_input, text="📂 1. Seleziona File Audio",
                                      command=self.select_file, fg_color="#E67E22", hover_color="#D35400")
        self.btn_file.pack(pady=10, padx=20, fill="x")

        # Waveform Frame
        self.frame_graph = ctk.CTkFrame(self, height=100, fg_color="#1a1a1a")
        self.frame_graph.pack(pady=5, padx=10, fill="x")
        self.lbl_instruction = ctk.CTkLabel(self.frame_graph, text="Il grafico apparirà qui", text_color="gray")
        self.lbl_instruction.place(relx=0.5, rely=0.5, anchor="center")

        # Sliders Controls
        self.create_cut_controls()

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(15, 5), padx=20, fill="x")
        self.progress_bar.pack_forget()

        # Start Button
        self.btn_process = ctk.CTkButton(self, text="🚀 2. AVVIA TRASCRIZIONE",
                                         font=("Arial", 16, "bold"), height=45,
                                         fg_color="#27AE60", hover_color="#2ECC71",
                                         state="disabled", command=self.start_thread_processing)
        self.btn_process.pack(pady=10, padx=20, fill="x")

        # Console Output
        self.textbox = ctk.CTkTextbox(self, width=800, height=150)
        self.textbox.pack(pady=10, padx=10, fill="both", expand=True)

    def create_cut_controls(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=5, padx=10, fill="x")

        # Start
        ctk.CTkLabel(frame, text="Inizio:").grid(row=0, column=0, padx=5)
        self.entry_start = ctk.CTkEntry(frame, width=70, justify="center")
        self.entry_start.grid(row=0, column=1)
        self.slider_start = ctk.CTkSlider(frame, from_=0, to=100, command=self.on_slider_start)
        self.slider_start.grid(row=0, column=2, padx=10, sticky="ew")

        # End
        ctk.CTkLabel(frame, text="Fine:").grid(row=1, column=0, padx=5)
        self.entry_end = ctk.CTkEntry(frame, width=70, justify="center")
        self.entry_end.grid(row=1, column=1)
        self.slider_end = ctk.CTkSlider(frame, from_=0, to=100, command=self.on_slider_end)
        self.slider_end.grid(row=1, column=2, padx=10, sticky="ew")

        frame.columnconfigure(2, weight=1)

    # --- LOGICA OPERATIVA ---
    def select_file(self):
        filename = filedialog.askopenfilename(filetypes=(("Audio", "*.mp3 *.wav *.m4a"), ("Tutti", "*.*")))
        if filename:
            self.lbl_instruction.destroy()
            duration = self.audio_handler.load_file(filename)
            self.setup_sliders(duration)
            self.draw_waveform()
            self.btn_process.configure(state="normal")
            self.textbox.insert("end", f"--> Caricato: {os.path.basename(filename)}\n")

    def setup_sliders(self, duration):
        self.slider_start.configure(to=duration)
        self.slider_start.set(0)
        self.slider_end.configure(to=duration)
        self.slider_end.set(duration)
        self.update_inputs()

    def update_inputs(self):
        self.entry_start.delete(0, "end")
        self.entry_start.insert(0, utils.seconds_to_hms(self.slider_start.get()))
        self.entry_end.delete(0, "end")
        self.entry_end.insert(0, utils.seconds_to_hms(self.slider_end.get()))

    def draw_waveform(self):
        data = self.audio_handler.get_waveform_data()
        for widget in self.frame_graph.winfo_children(): widget.destroy()

        fig = plt.Figure(figsize=(8, 1), dpi=100, facecolor='#1a1a1a')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1a1a')
        ax.plot(data, color='#E67E22', linewidth=0.6)
        ax.axis('off')
        fig.tight_layout(pad=0)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def on_slider_start(self, val):
        if val >= self.slider_end.get(): self.slider_end.set(val)
        self.update_inputs()

    def on_slider_end(self, val):
        if val <= self.slider_start.get(): self.slider_start.set(val)
        self.update_inputs()

    def start_thread_processing(self):
        if "gsk_" not in str(GROQ_API_KEY):
            messagebox.showerror("Errore", "Manca la API KEY nel codice o nel file .env!")
            return

        self.btn_process.configure(state="disabled", text="ELABORAZIONE...")
        self.progress_bar.pack(pady=(15, 5), padx=20, fill="x")
        self.progress_bar.set(0)
        self.textbox.delete("0.0", "end")

        threading.Thread(target=self.run_logic, args=(GROQ_API_KEY,)).start()

    def run_logic(self, api_key):
        try:
            self.transcriber.process_audio(
                self.audio_handler, self.slider_start.get(), self.slider_end.get(), api_key,
                self.update_progress, self.append_text
            )
            self.append_text("\n✨ TUTTO COMPLETATO!")

            # Esegue la callback per aggiornare la Libreria (nel thread principale)
            if self.on_complete_callback:
                self.after(0, self.on_complete_callback)

        except Exception as e:
            self.append_text(f"\n❌ ERRORE: {str(e)}")
        finally:
            self.btn_process.configure(state="normal", text="🚀 2. AVVIA TRASCRIZIONE")

    def update_progress(self, value):
        self.progress_bar.set(value)

    def append_text(self, text):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")
