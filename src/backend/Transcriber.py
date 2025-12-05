import os
import math
from utils import utils
from groq import Groq
from typing import Optional, Callable, Any


class Transcriber:
    """
    Gestisce il processo di trascrizione interfacciandosi con le API Cloud (Groq).
    Si occupa di preparare l'audio, dividerlo in segmenti per rispettare i limiti di upload,
    e ricomporre il testo finale.
    """

    def __init__(self):
        """Inizializza il transcriber."""
        pass

    def process_audio(self,
                      audio_handler: Any,
                      start_sec: float,
                      end_sec: float,
                      api_key: str,
                      output_filename: str,
                      progress_callback: Optional[Callable[[float], None]] = None,
                      text_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Esegue il flusso principale di trascrizione: taglio, chunking, invio API e unione risultati.

        Args:
            audio_handler (AudioHandler): L'istanza che contiene l'oggetto audio caricato.
            start_sec (float): Secondo di inizio del ritaglio.
            end_sec (float): Secondo di fine del ritaglio.
            api_key (str): La chiave API per autenticarsi su Groq.
            output_filename (str): Il nome desiderato per il file di output finale.
            progress_callback (Callable, optional): Funzione per aggiornare la barra di progresso (0.0 a 1.0).
            text_callback (Callable, optional): Funzione per scrivere log/testo nella console UI.

        Returns:
            str: Il testo completo trascritto.

        Raises:
            ValueError: Se nessun audio è stato caricato nell'handler.
        """
        if not audio_handler.audio:
            raise ValueError("Nessun audio caricato nell'AudioHandler.")

        # 1. Configurazione del Client API
        # Inizializziamo la connessione a Groq usando la chiave fornita.
        client = Groq(api_key=api_key)

        # 2. Preparazione del Segmento Audio
        # Pydub lavora in millisecondi, quindi convertiamo i secondi.
        # Questo crea un nuovo oggetto audio in memoria contenente solo la parte interessata.
        total_audio = audio_handler.audio[start_sec * 1000: end_sec * 1000]
        total_duration_ms = len(total_audio)

        # 3. Logica di Chunking (Spezzettamento)
        # Groq (come OpenAI) ha un limite di 25MB per file.
        # Un MP3 a 64kbit/s occupa circa 0.5 MB al minuto.
        # 20 minuti = ~10 MB, un margine di sicurezza molto ampio per evitare errori 413 (Payload Too Large).
        CHUNK_LENGTH_MS = 20 * 60 * 1000

        # Calcoliamo in quante parti dobbiamo dividere il file (arrotondando per eccesso)
        num_chunks = math.ceil(total_duration_ms / CHUNK_LENGTH_MS)
        full_transcript = ""

        if text_callback:
            text_callback(f"--> Audio diviso in {num_chunks} parti per rispettare i limiti API (25MB).\n")

        # 4. Elaborazione Sequenziale dei Chunk
        for i in range(num_chunks):
            # Calcolo degli indici di inizio e fine per il pezzo corrente
            chunk_start = i * CHUNK_LENGTH_MS
            chunk_end = min((i + 1) * CHUNK_LENGTH_MS, total_duration_ms)

            # Estrazione del chunk
            chunk = total_audio[chunk_start:chunk_end]
            temp_filename = f"temp_chunk_{i}.mp3"

            # Esportazione Temporanea
            # Usiamo bitrate="64k" per bilanciare qualità vocale e dimensione file ridotta.
            chunk.export(temp_filename, format="mp3", bitrate="64k")

            try:
                # Feedback Utente
                if text_callback:
                    text_callback(f"--> Elaborazione parte {i + 1}/{num_chunks}...")

                # Chiamata API Groq
                # Apriamo il file temporaneo in modalità binaria ('rb')
                with open(temp_filename, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(temp_filename, file.read()),
                        model="whisper-large-v3",  # Il modello SOTA per la trascrizione
                        response_format="json"  # JSON è più leggero e veloce da parsare del verbose_json
                    )

                segment_text = transcription.text
                full_transcript += segment_text + " "

                # Mostra anteprima live del testo ricevuto
                if text_callback:
                    text_callback(f"   [Parte {i + 1} OK]: {segment_text[:50]}...")

                # Aggiornamento Barra Progresso
                if progress_callback:
                    progress_callback((i + 1) / num_chunks)

            finally:
                # Pulizia: Rimuoviamo il file temporaneo per non intasare il disco
                # Il blocco 'finally' garantisce l'esecuzione anche se la chiamata API fallisce.
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        # 5. Salvataggio su File
        self.save_to_file(output_filename, full_transcript, text_callback)

        return full_transcript

    def save_to_file(self, filename_input: str, text: str, callback: Optional[Callable[[str], None]] = None):
        """
        Salva la trascrizione completa in un file di testo nella cartella centralizzata.

        Args:
            filename_input (str): Il nome del file (o percorso) scelto dall'utente o derivato dall'audio.
            text (str): Il contenuto testuale da salvare.
            callback (Callable, optional): Funzione per notificare l'avvenuto salvataggio.
        """
        try:
            # 1. Recupero della cartella di destinazione (Sbobinature)
            folder = utils.get_transcripts_folder()

            # 2. Sanitizzazione del nome file
            # os.path.basename assicura che prendiamo solo il nome file ed evitiamo percorsi malevoli
            filename_only = os.path.basename(filename_input)

            # Rimuoviamo l'estensione originale se presente (es. se l'input era "audio.mp3")
            base_name = os.path.splitext(filename_only)[0]

            # 3. Costruzione del percorso finale
            txt_path = os.path.join(folder, f"{base_name}.txt")

            # Scrittura del file (UTF-8 per supportare caratteri speciali ed emoji)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            if callback:
                callback(f"\n✅ SALVATO IN LIBRERIA:\n{base_name}.txt")

        except Exception as e:
            if callback:
                callback(f"❌ Errore critico durante il salvataggio: {e}")
            # È buona norma stampare l'errore anche su console per debug
            print(f"Error saving file: {e}")