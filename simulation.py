from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
import time

class AccelerometerSimulator(QObject):
    """
    Simulates accelerometer signals for multiple sensors and emits data in real time.

    This class runs in a separate thread to continuously generate synthetic vibration
    signals composed of multiple sine waves with noise, mimicking real sensor outputs.
    The data_ready signal sends batches of data as numpy arrays to the GUI or processing pipeline.
    The finished signal notifies when the simulation stops.

    Attributes:
        sensor_count (int): Number of sensors to simulate.
        freq (int): Sampling frequency in Hz.
        buffer_len (int): Number of samples generated per batch.
        running (bool): Control flag for simulation loop.
    """
    data_ready = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, sensor_count=4, freq=1000, buffer_len=1024):
        super().__init__()
        self.sensor_count = sensor_count
        self.freq = freq
        self.buffer_len = buffer_len
        self.running = False

    def run(self):
        self.running = True
        start_sample = 0
        while self.running:
            # Time vector for this batch of samples
            t = (np.arange(self.buffer_len) + start_sample) / self.freq
            signals = []
            for i in range(self.sensor_count):
                # Generate a composite vibration signal for each sensor
                # used several sine waves with increasing frequency and noise to simulate realistic data
                s = (0.5 + i) * np.sin(2 * np.pi * (10 + i*5) * t) \
                    + 0.3 * np.sin(2 * np.pi * (20 + i*3) * t) \
                    + 0.1 * np.sin(2 * np.pi * (30 + i*2) * t)
                s += np.random.normal(0, 0.2, size=t.shape)
                signals.append(s)
            # Emit the batch of simulated signals to be received by GUI or processing
            self.data_ready.emit(np.array(signals))
            start_sample += self.buffer_len  # advance for next batch
            time.sleep(self.buffer_len / self.freq)


    def stop(self):
        # Stop the simulation loop and notify that simulation has finished
        self.running = False
        self.finished.emit()
