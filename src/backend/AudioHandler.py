import numpy as np
from pydub import AudioSegment

class AudioHandler:
    def __init__(self):
        self.audio = None
        self.duration = 0
        self.filepath = None

    def load_file(self, filepath):
        self.filepath = filepath
        self.audio = AudioSegment.from_file(filepath)
        self.duration = len(self.audio) / 1000.0
        return self.duration

    def get_waveform_data(self, max_points=5000):
        if not self.audio: return []
        raw_data = np.array(self.audio.get_array_of_samples())
        if self.audio.channels == 2: raw_data = raw_data[::2]
        if len(raw_data) > max_points:
            step = int(len(raw_data) / max_points)
            raw_data = raw_data[::step]
        return raw_data