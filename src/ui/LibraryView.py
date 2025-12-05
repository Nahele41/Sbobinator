import os
import platform
import subprocess
from tkinter import messagebox

import customtkinter as ctk

from utils import utils

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LibraryView(ctk.CTkFrame):
    """
    Gestisce la visualizzazione dei file trascritti, l'export e l'eliminazione.
    """

    def __init__(self, master):
        super().__init__(master)
        self.selected_file_path = None
        self.create_ui()
        self.refresh_library()  # Caricamento iniziale

    def create_ui(self):
        # Struttura a colonne
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # -- Colonna Sinistra: Lista --
        self.scroll_files = ctk.CTkScrollableFrame(self, label_text="Trascrizioni Disponibili")
        self.scroll_files.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # -- Colonna Destra: Azioni --
        self.frame_actions = ctk.CTkFrame(self)
        self.frame_actions.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frame_actions, text="Azioni File", font=("Arial", 18, "bold")).pack(pady=20)

        self.lbl_selected = ctk.CTkLabel(self.frame_actions, text="Nessun file selezionato", text_color="gray",
                                         wraplength=180)
        self.lbl_selected.pack(pady=10)

        # Pulsanti Export
        self.btn_open = ctk.CTkButton(self.frame_actions, text="📄 Apri Testo", state="disabled", command=self.open_file)
        self.btn_open.pack(pady=5, padx=20, fill="x")

        self.btn_pdf = ctk.CTkButton(self.frame_actions, text="🔴 Export PDF", fg_color="#C0392B", state="disabled",
                                     command=lambda: self.export_file("pdf"))
        self.btn_pdf.pack(pady=5, padx=20, fill="x")

        self.btn_word = ctk.CTkButton(self.frame_actions, text="🔵 Export WORD", fg_color="#2980B9", state="disabled",
                                      command=lambda: self.export_file("word"))
        self.btn_word.pack(pady=5, padx=20, fill="x")

        self.btn_ics = ctk.CTkButton(self.frame_actions, text="Chiedi a Nahele un altro formato :)", fg_color="#8E44AD",
                                     state="disabled")  # Nota: era active nel tuo codice, messo disabled per coerenza
        self.btn_ics.pack(pady=5, padx=20, fill="x")

        # Spacer
        ctk.CTkLabel(self.frame_actions, text="").pack(pady=10)

        # Pulsante ELIMINA
        self.btn_delete = ctk.CTkButton(self.frame_actions, text="🗑️ ELIMINA", fg_color="#7B241C",
                                        hover_color="#561914", state="disabled", command=self.delete_selected_file)
        self.btn_delete.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(self.frame_actions, text="🔄 Aggiorna Lista", fg_color="gray", command=self.refresh_library).pack(
            pady=20, padx=20, fill="x")

    def refresh_library(self):
        # Pulisce la UI
        for widget in self.scroll_files.winfo_children():
            widget.destroy()

        folder = utils.get_transcripts_folder()
        try:
            files = [f for f in os.listdir(folder) if not f.startswith(".")]  # Ignora file nascosti tipo .DS_Store
        except FileNotFoundError:
            files = []

        if not files:
            ctk.CTkLabel(self.scroll_files, text="Archivio vuoto.").pack(pady=10)
            self.lbl_selected.configure(text="Nessun file")
            self.disable_buttons()
            return

        # Ordina per data
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)

        for f in files:
            full_path = os.path.join(folder, f)
            btn = ctk.CTkButton(self.scroll_files, text=f, fg_color="transparent", border_width=1,
                                text_color=("gray10", "gray90"), anchor="w",
                                command=lambda x=full_path: self.select_library_item(x))
            btn.pack(fill="x", pady=2, padx=5)

    def select_library_item(self, filepath):
        if os.path.exists(filepath):
            self.selected_file_path = filepath
            self.lbl_selected.configure(text=os.path.basename(filepath), text_color="white")
            self.enable_buttons()
        else:
            self.refresh_library()

    def enable_buttons(self):
        self.btn_open.configure(state="normal")
        self.btn_pdf.configure(state="normal")
        self.btn_word.configure(state="normal")
        self.btn_ics.configure(state="normal")  # Riattiva se vuoi implementare la logica
        self.btn_delete.configure(state="normal")

    def disable_buttons(self):
        self.selected_file_path = None
        self.btn_open.configure(state="disabled")
        self.btn_pdf.configure(state="disabled")
        self.btn_word.configure(state="disabled")
        self.btn_ics.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

    def delete_selected_file(self):
        if not self.selected_file_path: return
        filename = os.path.basename(self.selected_file_path)
        if messagebox.askyesno("Conferma", f"Vuoi eliminare:\n{filename}?"):
            try:
                os.remove(self.selected_file_path)
                self.refresh_library()
                self.disable_buttons()
                self.lbl_selected.configure(text="File eliminato.", text_color="red")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile eliminare: {e}")

    def open_file(self):
        if self.selected_file_path:
            if platform.system() == 'Darwin':
                subprocess.call(('open', self.selected_file_path))
            elif platform.system() == 'Windows':
                os.startfile(self.selected_file_path)

    def export_file(self, format_type):
        if not self.selected_file_path or not self.selected_file_path.endswith(".txt"):
            messagebox.showerror("Errore", "Seleziona un file .txt valido")
            return

        try:
            with open(self.selected_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            new_path = ""
            if format_type == "pdf":
                new_path = utils.save_as_pdf(content, self.selected_file_path)
            elif format_type == "word":
                new_path = utils.save_as_docx(content, self.selected_file_path)
            # elif format_type == "ics": ...

            messagebox.showinfo("Export Riuscito", f"File creato:\n{os.path.basename(new_path)}")
            # Aggiorniamo la lista perché il nuovo file creato (es. pdf) deve apparire
            self.refresh_library()
        except Exception as e:
            messagebox.showerror("Errore Export", str(e))