import numpy as np

def compute_fft(signal, sample_rate):
    """
    This function computes the one-sided FFT of a signal.

    Arguments:
        signal (np.ndarray): Input time-domain signal samples.
        sample_rate (float): Sampling frequency in Hz.

    Returns:
        tuple: Frequencies (Hz) and corresponding FFT magnitudes.
    """
    N = len(signal)
    freqs = np.fft.rfftfreq(N, d=1/sample_rate)
    fft_vals = np.abs(np.fft.rfft(signal))
    return freqs, fft_vals

def compute_rms(signal):
    """
    This function calculates the root mean square (RMS) value of a given signal.

    Arguments:
        signal (np.ndarray): Input time-domain signal samples.

    Returns:
        float: RMS value, representing signal's effective magnitude.
    """
    return np.sqrt(np.mean(signal**2))
