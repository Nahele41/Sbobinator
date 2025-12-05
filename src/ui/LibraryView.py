import os
import platform
import subprocess
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from utils import utils

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class LibraryView(ctk.CTkFrame):
    """
    Gestisce l'interfaccia utente per la libreria delle trascrizioni.

    Permette di:
    - Visualizzare l'elenco dei file salvati nella cartella 'Sbobinature'.
    - Aprire i file con l'editor di sistema.
    - Esportare i file in altri formati (PDF, Word).
    - Eliminare i file.
    """

    def __init__(self, master):
        """
        Inizializza la vista della libreria.

        Args:
            master: Il widget genitore (solitamente un CTkTabview o CTkFrame).
        """
        super().__init__(master)

        # Variabile di stato per tracciare quale file è attualmente evidenziato
        self.selected_file_path: Optional[str] = None

        self.create_ui()

        # Popola la lista appena l'app si avvia
        self.refresh_library()

    def create_ui(self):
        """Costruisce il layout grafico a due colonne (Lista vs Azioni)."""

        # Configurazione Grid:
        # Colonna 0 (Lista) pesa doppio (weight=2) rispetto alla Colonna 1 (Azioni)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # -- Colonna Sinistra: Lista File --
        self.scroll_files = ctk.CTkScrollableFrame(self, label_text="Trascrizioni Disponibili")
        self.scroll_files.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # -- Colonna Destra: Pannello Azioni --
        self.frame_actions = ctk.CTkFrame(self)
        self.frame_actions.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frame_actions, text="Azioni File", font=("Arial", 18, "bold")).pack(pady=20)

        # Label per mostrare il nome del file selezionato
        self.lbl_selected = ctk.CTkLabel(self.frame_actions, text="Nessun file selezionato", text_color="gray",
                                         wraplength=180)
        self.lbl_selected.pack(pady=10)

        # --- Pulsanti Export e Gestione ---
        # Inizialmente disabilitati finché non si seleziona un file
        self.btn_open = ctk.CTkButton(self.frame_actions, text="📄 Apri Testo", state="disabled", command=self.open_file)
        self.btn_open.pack(pady=5, padx=20, fill="x")

        self.btn_pdf = ctk.CTkButton(self.frame_actions, text="🔴 Export PDF", fg_color="#C0392B", state="disabled",
                                     command=lambda: self.export_file("pdf"))
        self.btn_pdf.pack(pady=5, padx=20, fill="x")

        self.btn_word = ctk.CTkButton(self.frame_actions, text="🔵 Export WORD", fg_color="#2980B9", state="disabled",
                                      command=lambda: self.export_file("word"))
        self.btn_word.pack(pady=5, padx=20, fill="x")

        # Pulsante placeholder per formati futuri (ICS o altro)
        self.btn_ics = ctk.CTkButton(self.frame_actions, text="Chiedi a Nahele un altro formato :)", fg_color="#8E44AD",
                                     state="disabled")
        self.btn_ics.pack(pady=5, padx=20, fill="x")

        # Spacer visivo
        ctk.CTkLabel(self.frame_actions, text="").pack(pady=10)

        # Pulsante ELIMINA (Rosso scuro per indicare pericolo)
        self.btn_delete = ctk.CTkButton(self.frame_actions, text="🗑️ ELIMINA", fg_color="#7B241C",
                                        hover_color="#561914", state="disabled", command=self.delete_selected_file)
        self.btn_delete.pack(pady=10, padx=20, fill="x")

        # Pulsante Aggiorna Manuale
        ctk.CTkButton(self.frame_actions, text="🔄 Aggiorna Lista", fg_color="gray", command=self.refresh_library).pack(
            pady=20, padx=20, fill="x")

    def refresh_library(self):
        """
        Scansiona la cartella 'Sbobinature' e rigenera i pulsanti nella lista.
        Gestisce anche il filtraggio di file nascosti e l'ordinamento temporale.
        """
        # 1. Pulisce la UI rimuovendo tutti i vecchi pulsanti
        for widget in self.scroll_files.winfo_children():
            widget.destroy()

        folder = utils.get_transcripts_folder()
        try:
            # List comprehension per filtrare file di sistema (es. .DS_Store su Mac)
            files = [f for f in os.listdir(folder) if not f.startswith(".")]
        except FileNotFoundError:
            files = []

        # Se non ci sono file, mostra un avviso e resetta i controlli
        if not files:
            ctk.CTkLabel(self.scroll_files, text="Archivio vuoto.").pack(pady=10)
            self.lbl_selected.configure(text="Nessun file")
            self.disable_buttons()
            return

        # 2. Ordinamento: Dal più recente al più vecchio (Best UX)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)

        # 3. Creazione dinamica dei pulsanti per ogni file
        for f in files:
            full_path = os.path.join(folder, f)
            # Usiamo una lambda con default argument (x=full_path) per "congelare" il valore della variabile
            btn = ctk.CTkButton(self.scroll_files, text=f, fg_color="transparent", border_width=1,
                                text_color=("gray10", "gray90"), anchor="w",
                                command=lambda x=full_path: self.select_library_item(x))
            btn.pack(fill="x", pady=2, padx=5)

    def select_library_item(self, filepath: str):
        """
        Gestisce il click su un file nella lista.

        Args:
            filepath (str): Il percorso completo del file selezionato.
        """
        # Verifica di sicurezza: il file potrebbe essere stato cancellato esternamente
        if os.path.exists(filepath):
            self.selected_file_path = filepath
            self.lbl_selected.configure(text=os.path.basename(filepath), text_color="white")
            self.enable_buttons()
        else:
            # Se il file non esiste più, aggiorniamo la lista per riflettere la realtà
            self.refresh_library()

    def enable_buttons(self):
        """Abilita i pulsanti di azione quando un file è selezionato."""
        self.btn_open.configure(state="normal")
        self.btn_pdf.configure(state="normal")
        self.btn_word.configure(state="normal")
        self.btn_ics.configure(state="normal")
        self.btn_delete.configure(state="normal")

    def disable_buttons(self):
        """Disabilita i pulsanti di azione (stato iniziale o post-cancellazione)."""
        self.selected_file_path = None
        self.btn_open.configure(state="disabled")
        self.btn_pdf.configure(state="disabled")
        self.btn_word.configure(state="disabled")
        self.btn_ics.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

    def delete_selected_file(self):
        """
        Elimina il file selezionato dal disco, chiedendo prima conferma all'utente.
        """
        if not self.selected_file_path: return

        filename = os.path.basename(self.selected_file_path)

        # Popup di conferma
        if messagebox.askyesno("Conferma", f"Vuoi eliminare definitivamente:\n{filename}?"):
            try:
                os.remove(self.selected_file_path)

                # Feedback visivo
                self.refresh_library()
                self.disable_buttons()
                self.lbl_selected.configure(text="File eliminato.", text_color="red")

            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile eliminare: {e}")

    def open_file(self):
        """
        Apre il file di testo selezionato utilizzando l'applicazione predefinita del sistema operativo.
        Supporta Windows e macOS.
        """
        if self.selected_file_path:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', self.selected_file_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(self.selected_file_path)

    def export_file(self, format_type: str):
        """
        Avvia il processo di esportazione del file di testo in un altro formato.

        Args:
            format_type (str): Il formato target ('pdf', 'word', etc.).
        """
        if not self.selected_file_path or not self.selected_file_path.endswith(".txt"):
            messagebox.showerror("Errore", "Seleziona un file .txt valido")
            return

        try:
            # Leggiamo il contenuto del file
            with open(self.selected_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            new_path = ""
            # Deleghiamo la conversione al modulo utils
            if format_type == "pdf":
                new_path = utils.save_as_pdf(content, self.selected_file_path)
            elif format_type == "word":
                new_path = utils.save_as_docx(content, self.selected_file_path)
            # elif format_type == "ics": ... # Logica futura

            messagebox.showinfo("Export Riuscito", f"File creato:\n{os.path.basename(new_path)}")

            # Aggiorniamo la lista affinché il nuovo file (es. PDF) appaia se decidiamo di mostrarli
            self.refresh_library()

        except Exception as e:
            messagebox.showerror("Errore Export", str(e))