import customtkinter as ctk

from ui.LibraryView import LibraryView
from ui.TranscribeView import TranscribeView

# Configurazione globale dell'aspetto (Global State)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class SpeechToTextApp(ctk.CTk):
    """
    Classe Principale (Entry Point) dell'applicazione 'Ultimate Sbobinator'.

    Questa classe estende ctk.CTk (la finestra principale) e funge da Container.
    Implementa un pattern architetturale simile all'MVC (Model-View-Controller) dove:
    - Main: Orchestratore che gestisce il layout generale e le Tab.
    - Views: (LibraryView, TranscribeView) gestiscono la logica di presentazione specifica.
    - Callback: Vengono passati tra le viste per permettere la comunicazione disaccoppiata.
    """

    def __init__(self):
        """
        Inizializza l'applicazione, configura la finestra principale e istanzia le Viste.
        """
        super().__init__()

        # Configurazione Finestra
        self.title("Ultimate Sbobinator Turbo Deluxe 5000")
        self.geometry("950x750")

        # --- TABVIEW (Gestore Schede) ---
        # Usiamo un TabView per separare logicamente le due funzionalità principali
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(pady=10, padx=10, fill="both", expand=True)

        # Creazione dei frame per i tab
        self.tab_transcribe_frame = self.tab_view.add("🎙️ Nuova Trascrizione")
        self.tab_library_frame = self.tab_view.add("📚 Libreria & Export")

        # --- INIZIALIZZAZIONE DELLE VISTE ---

        # 1. Istanziazione della Vista Libreria
        # La inseriamo nel secondo tab. Questa vista gestisce file e export.
        self.library_view = LibraryView(master=self.tab_library_frame)
        self.library_view.pack(fill="both", expand=True)

        # 2. Istanziazione della Vista Trascrizione
        # La inseriamo nel primo tab.
        # CRUCIALE: Passiamo 'self.library_view.refresh_library' come callback.
        # In questo modo, quando TranscribeView finisce un lavoro, può "notificare"
        # la LibraryView di aggiornare la lista, senza che le due classi siano
        # strettamente accoppiate o si conoscano direttamente.
        self.transcribe_view = TranscribeView(
            master=self.tab_transcribe_frame,
            on_complete_callback=self.library_view.refresh_library
        )
        self.transcribe_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    # Blocco di esecuzione standard
    app = SpeechToTextApp()
    app.mainloop()