from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
import time

class AccelerometerSimulator(QObject):
    data_ready = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, sensor_count=4, freq=100, buffer_len=1024):
        super().__init__()
        self.sensor_count = sensor_count
        self.freq = freq
        self.buffer_len = buffer_len
        self.running = False

    def run(self):
        self.running = True
        start_sample = 0
        while self.running:
            t = (np.arange(self.buffer_len) + start_sample) / self.freq
            signals = []
            for i in range(self.sensor_count):
                s = (0.5 + i) * np.sin(2 * np.pi * (10 + i*5) * t) \
                    + 0.3 * np.sin(2 * np.pi * (20 + i*3) * t) \
                    + 0.1 * np.sin(2 * np.pi * (30 + i*2) * t)
                s += np.random.normal(0, 0.2, size=t.shape)
                signals.append(s)
            self.data_ready.emit(np.array(signals))
            start_sample += self.buffer_len  # advance for next batch
            time.sleep(self.buffer_len / self.freq)


    def stop(self):
        self.running = False
        self.finished.emit()
