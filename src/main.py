import customtkinter as ctk

from ui.LibraryView import LibraryView
from ui.TranscribeView import TranscribeView

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SpeechToTextApp(ctk.CTk):
    """
    Classe Main: Crea la finestra e gestisce le due View separate
    """
    def __init__(self):
        super().__init__()

        self.title("Ultimate Sbobinator Turbo Deluxe 5000")
        self.geometry("950x750")

        # --- TABVIEW ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(pady=10, padx=10, fill="both", expand=True)

        # Creazione dei tab
        self.tab_transcribe_frame = self.tab_view.add("🎙️ Nuova Trascrizione")
        self.tab_library_frame = self.tab_view.add("📚 Libreria & Export")

        # Inizializzazione delle View
        # 1. Istanziamo la Libreria
        self.library_view = LibraryView(master=self.tab_library_frame)
        self.library_view.pack(fill="both", expand=True)

        # 2. Istanziamo la Trascrizione
        # Passiamo library_view.refresh_library come callback!
        # Così quando la trascrizione finisce, la view chiama questa funzione per aggiornare la lista.
        self.transcribe_view = TranscribeView(
            master=self.tab_transcribe_frame,
            on_complete_callback=self.library_view.refresh_library
        )
        self.transcribe_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = SpeechToTextApp()
    app.mainloop()