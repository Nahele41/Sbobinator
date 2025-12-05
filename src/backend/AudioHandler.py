import numpy as np
from pydub import AudioSegment
from typing import Optional, List, Union


class AudioHandler:
    """
    Gestisce le operazioni sui file audio, inclusi il caricamento,
    il calcolo della durata e l'estrazione dei dati per la visualizzazione della forma d'onda.
    """

    def __init__(self):
        """Inizializza l'handler con uno stato vuoto."""
        self.audio: Optional[AudioSegment] = None
        self.duration: float = 0.0
        self.filepath: Optional[str] = None

    def load_file(self, filepath: str) -> float:
        """
        Carica un file audio dal percorso specificato utilizzando Pydub.

        Args:
            filepath (str): Il percorso assoluto o relativo del file audio.

        Returns:
            float: La durata totale dell'audio in secondi.
        """
        self.filepath = filepath

        # Carica il file audio (Pydub gestisce automaticamente formati come mp3, wav, m4a)
        self.audio = AudioSegment.from_file(filepath)

        # Pydub calcola la lunghezza in millisecondi, convertiamo in secondi per l'UI
        self.duration = len(self.audio) / 1000.0

        return self.duration

    def get_waveform_data(self, max_points: int = 5000) -> Union[List, np.ndarray]:
        """
        Estrae e campiona i dati audio per la visualizzazione grafica nell'UI.

        Per mantenere l'interfaccia reattiva, questo metodo riduce (downsampling)
        il numero di campioni a un massimo prefissato.

        Args:
            max_points (int): Numero massimo di punti da restituire per il grafico.
                              Default a 5000.

        Returns:
            np.ndarray: Un array numpy contenente i dati di ampiezza audio campionati.
                        Restituisce una lista vuota se nessun audio è caricato.
        """
        if not self.audio:
            return []

        # Ottiene i campioni grezzi (raw samples) come array numpy
        raw_data = np.array(self.audio.get_array_of_samples())

        # Gestione Stereo: Se l'audio ha 2 canali, prendiamo solo un canale (es. sinistro)
        # o alterniamo i campioni per semplificare il grafico a una sola linea.
        if self.audio.channels == 2:
            raw_data = raw_data[::2]

        # Downsampling: Se i dati superano i punti massimi consentiti, calcoliamo uno "step"
        # per saltare i campioni e ridurre il peso computazionale del grafico.
        if len(raw_data) > max_points:
            step = int(len(raw_data) / max_points)
            raw_data = raw_data[::step]

        return raw_data