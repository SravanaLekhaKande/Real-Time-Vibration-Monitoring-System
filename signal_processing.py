import numpy as np

def compute_fft(signal, sample_rate):
    N = len(signal)
    freqs = np.fft.rfftfreq(N, d=1/sample_rate)
    fft_vals = np.abs(np.fft.rfft(signal))
    return freqs, fft_vals

def compute_rms(signal):
    return np.sqrt(np.mean(signal**2))
