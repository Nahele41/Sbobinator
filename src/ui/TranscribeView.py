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

# --- CONFIGURAZIONE ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class TranscribeView(ctk.CTkFrame):
    """
        Gestisce la scheda 'Nuova Trascrizione' dell'applicazione.

        Responsabilità principali:
        - Caricamento e validazione del file audio.
        - Visualizzazione grafica della forma d'onda (Waveform).
        - Controlli per il ritaglio (Start/End).
        - Avvio del processo di trascrizione in un thread separato.
        - Gestione dell'input utente per il nome del file di output.
        """
    def __init__(self, master, on_complete_callback=None):
        """
            Inizializza la vista di trascrizione.

            Args:
                master: Il widget genitore.
                on_complete_callback (Callable, optional): Funzione da chiamare al termine
                                                           della trascrizione (es. per aggiornare la libreria).
        """
        super().__init__(master)

        self.on_complete_callback = on_complete_callback

        # Inizializzazione dei moduli di backend
        self.audio_handler = AudioHandler.AudioHandler()
        self.transcriber = Transcriber.Transcriber()

        # Setup una tantum per FFmpeg (percorsi di sistema)
        utils.setup_ffmpeg()

        self.create_ui()

    def create_ui(self):
        """
        Costruisce i widget dell'interfaccia utente.
        """

        # Titolo
        ctk.CTkLabel(self, text="Ultimate Sbobinator Turbo Deluxe 5000", font=("Arial", 24, "bold")).pack(pady=10)

        # --- Sezione Input File ---
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.pack(pady=10, padx=10, fill="x")

        self.btn_file = ctk.CTkButton(self.frame_input, text="📂 1. Seleziona File Audio",
                                      command=self.select_file, fg_color="#E67E22", hover_color="#D35400")
        self.btn_file.pack(pady=10, padx=20, fill="x")

        # --- Sezione Grafico (Waveform) ---
        self.frame_graph = ctk.CTkFrame(self, height=100, fg_color="#1a1a1a")
        self.frame_graph.pack(pady=5, padx=10, fill="x")
        self.lbl_instruction = ctk.CTkLabel(self.frame_graph, text="Il grafico apparirà qui", text_color="gray")
        self.lbl_instruction.place(relx=0.5, rely=0.5, anchor="center")

        # Controlli di ritaglio (Slider)
        self.create_cut_controls()

        # Barra di Progresso (Nascosta inizialmente)
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(15, 5), padx=20, fill="x")
        self.progress_bar.pack_forget()

        # Pulsante Avvio Trascrizione
        self.btn_process = ctk.CTkButton(self, text="🚀 2. AVVIA TRASCRIZIONE",
                                         font=("Arial", 16, "bold"), height=45,
                                         fg_color="#27AE60", hover_color="#2ECC71",
                                         state="disabled", command=self.start_thread_processing)
        self.btn_process.pack(pady=10, padx=20, fill="x")

        # Console di Log
        self.textbox = ctk.CTkTextbox(self, width=800, height=150)
        self.textbox.pack(pady=10, padx=10, fill="both", expand=True)

    def create_cut_controls(self):
        """
        Crea i controlli (Slider ed Entry) per selezionare inizio e fine audio.
        """
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=5, padx=10, fill="x")

        # Start Controls
        ctk.CTkLabel(frame, text="Inizio:").grid(row=0, column=0, padx=5)
        self.entry_start = ctk.CTkEntry(frame, width=70, justify="center")
        self.entry_start.grid(row=0, column=1)
        self.slider_start = ctk.CTkSlider(frame, from_=0, to=100, command=self.on_slider_start)
        self.slider_start.grid(row=0, column=2, padx=10, sticky="ew")

        # End Controls
        ctk.CTkLabel(frame, text="Fine:").grid(row=1, column=0, padx=5)
        self.entry_end = ctk.CTkEntry(frame, width=70, justify="center")
        self.entry_end.grid(row=1, column=1)
        self.slider_end = ctk.CTkSlider(frame, from_=0, to=100, command=self.on_slider_end)
        self.slider_end.grid(row=1, column=2, padx=10, sticky="ew")

        frame.columnconfigure(2, weight=1)

    def select_file(self):
        """
        Apre il file dialog, carica l'audio nel backend e aggiorna la UI.
        """
        filename = filedialog.askopenfilename(filetypes=(("Audio", "*.mp3 *.wav *.m4a"), ("Tutti", "*.*")))

        if filename:
            # Rimuove l'istruzione placeholder
            self.lbl_instruction.destroy()

            # Carica audio e ottiene durata
            duration = self.audio_handler.load_file(filename)

            # Aggiorna UI
            self.setup_sliders(duration)
            self.draw_waveform()
            self.btn_process.configure(state="normal")

            self.textbox.insert("end", f"--> Caricato: {os.path.basename(filename)}\n")

    def setup_sliders(self, duration):
        """
        Configura i limiti degli slider in base alla durata del file.
        """
        self.slider_start.configure(to=duration)
        self.slider_start.set(0)
        self.slider_end.configure(to=duration)
        self.slider_end.set(duration)
        self.update_inputs()

    def update_inputs(self):
        """
            Sincronizza le caselle di testo (HH:MM:SS) con il valore attuale degli slider.
        """
        self.entry_start.delete(0, "end")
        self.entry_start.insert(0, utils.seconds_to_hms(self.slider_start.get()))
        self.entry_end.delete(0, "end")
        self.entry_end.insert(0, utils.seconds_to_hms(self.slider_end.get()))

    def draw_waveform(self):
        """
            Disegna la forma d'onda dell'audio usando Matplotlib integrato in Tkinter.
        """
        data = self.audio_handler.get_waveform_data()

        # Pulizia grafico precedente per evitare sovrapposizioni e memory leak
        for widget in self.frame_graph.winfo_children(): widget.destroy()

        # Configurazione Matplotlib
        fig = plt.Figure(figsize=(8, 1), dpi=100, facecolor='#1a1a1a')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1a1a')
        ax.plot(data, color='#E67E22', linewidth=0.6)
        ax.axis('off') # Nasconde gli assi per un look più pulito
        fig.tight_layout(pad=0)

        # Rendering nel widget CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def on_slider_start(self, val):
        """
        Callback slider Inizio: impedisce che l'inizio superi la fine.
        """
        if val >= self.slider_end.get(): self.slider_end.set(val)
        self.update_inputs()

    def on_slider_end(self, val):
        """
        Callback slider Fine: impedisce che la fine preceda l'inizio.
        """
        if val <= self.slider_start.get(): self.slider_start.set(val)
        self.update_inputs()

    def start_thread_processing(self):
        """
        Avvia la procedura di trascrizione.
        1. Verifica la chiave API.
        2. Chiede il nome del file di output (Popup).
        3. Avvia il thread di elaborazione (per non bloccare la GUI).
        """
        if "gsk_" not in str(GROQ_API_KEY):
            messagebox.showerror("Errore", "Manca la API KEY nel file .env!")
            return

        # --- 1. POPUP PER IL NOME FILE ---
        default_name = os.path.splitext(os.path.basename(self.audio_handler.filepath))[0]

        dialog = ctk.CTkInputDialog(text=f"Nome del file di output?\n(Lascia vuoto per: {default_name})",
                                    title="Salva come...")
        custom_name = dialog.get_input()  # Questa funzione blocca il codice finché l'utente non risponde

        # Se l'utente preme "Annulla" o chiude la finestra, custom_name è None -> Interrompiamo
        if custom_name is None:
            return

        # Se l'utente preme "OK" ma lascia vuoto, usiamo il nome di default
        if custom_name.strip() == "":
            custom_name = default_name

        # --- 2. PREPARAZIONE UI ---
        self.btn_process.configure(state="disabled", text="ELABORAZIONE...")
        self.progress_bar.pack(pady=(15, 5), padx=20, fill="x")
        self.progress_bar.set(0)
        self.textbox.delete("0.0", "end")

        # --- 3. AVVIO THREAD ---
        threading.Thread(target=self.run_logic, args=(GROQ_API_KEY, custom_name)).start()

    def run_logic(self, api_key, custom_filename):
        """
        Logica eseguita nel thread separato.
        Chiama il backend e gestisce il ciclo di vita della trascrizione.
        """
        try:
            self.transcriber.process_audio(
                self.audio_handler,
                self.slider_start.get(),
                self.slider_end.get(),
                api_key,
                output_filename=custom_filename,
                progress_callback=self.update_progress,
                text_callback=self.append_text
            )

            self.append_text("\n✨ TUTTO COMPLETATO!")

            # Notifica la view principale (se il callback esiste) usando .after per thread-safety
            if self.on_complete_callback:
                self.after(0, self.on_complete_callback)

        except Exception as e:
            self.append_text(f"\n❌ ERRORE: {str(e)}")
        finally:
            # Ripristina lo stato del pulsante nel thread principale
            self.btn_process.configure(state="normal", text="🚀 2. AVVIA TRASCRIZIONE")

    def update_progress(self, value):
        """
        Aggiorna la barra di progresso (Thread-safe).
        """
        self.progress_bar.set(value)

    def append_text(self, text):
        """
        Scrive nella console di log e scrolla in basso.
        """
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

