import math
import os

from groq import Groq
from  utils import utils

class Transcriber:
    def __init__(self):
        pass

    def process_audio(self, audio_handler, start_sec, end_sec, api_key, progress_callback=None, text_callback=None):
        """
        Gestisce il taglio intelligente e l'invio a Groq in chunk.
        """
        if not audio_handler.audio:
            raise ValueError("Nessun audio caricato")

        # 1. Configura Client Groq
        client = Groq(api_key=api_key)

        # 2. Prepara il segmento totale selezionato dall'utente
        total_audio = audio_handler.audio[start_sec * 1000: end_sec * 1000]
        total_duration_ms = len(total_audio)

        # 3. Definisci la dimensione del chunk (es. 20 minuti = 1200000 ms)
        # 20 min in MP3 64k sono circa 9.6MB, sicurissimo per il limite di 25MB
        CHUNK_LENGTH_MS = 20 * 60 * 1000

        num_chunks = math.ceil(total_duration_ms / CHUNK_LENGTH_MS)
        full_transcript = ""

        text_callback(f"--> Audio diviso in {num_chunks} parti per rispettare i limiti API.\n")

        # 4. Ciclo sui pezzi
        for i in range(num_chunks):
            chunk_start = i * CHUNK_LENGTH_MS
            chunk_end = min((i + 1) * CHUNK_LENGTH_MS, total_duration_ms)

            # Estrai il pezzo
            chunk = total_audio[chunk_start:chunk_end]
            temp_filename = f"temp_chunk_{i}.mp3"

            # Esporta in MP3 leggero
            chunk.export(temp_filename, format="mp3", bitrate="64k")

            try:
                # Aggiorna UI
                text_callback(f"--> Elaborazione parte {i + 1}/{num_chunks}...")

                # Chiama Groq
                with open(temp_filename, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(temp_filename, file.read()),
                        model="whisper-large-v3",
                        response_format="json"  # Usiamo json semplice per velocità
                    )

                segment_text = transcription.text
                full_transcript += segment_text + " "

                # Mostra anteprima testo live
                text_callback(f"   [Parte {i + 1} OK]: {segment_text[:50]}...")

                # Aggiorna Barra Progresso (valore da 0 a 1)
                if progress_callback:
                    progress_callback((i + 1) / num_chunks)

            finally:
                # Pulizia immediata del chunk
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        # 5. Salvataggio finale
        self.save_to_file(audio_handler.filepath, full_transcript, text_callback)
        return full_transcript

    def save_to_file(self, original_audio_path, text, callback):
        try:
            # 1. Recuperiamo la cartella centralizzata
            folder = utils.get_transcripts_folder()

            # 2. Estraiamo solo il nome del file (es. "lezione.mp3") senza percorso
            filename_only = os.path.basename(original_audio_path)
            base_name = os.path.splitext(filename_only)[0]

            # 3. Costruiamo il percorso finale dentro "Sbobinature"
            txt_path = os.path.join(folder, f"{base_name}_transcript.txt")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            callback(f"\n✅ SALVATO IN LIBRERIA:\n{base_name}_transcript.txt")

        except Exception as e:
            callback(f"❌ Errore salvataggio: {e}")
            print(e)