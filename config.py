class Config:
    # Number of sensors going to be simulated/displayed in the GUI.
    SENSOR_COUNT = 4

    # Data sampling frequency in Hz (samples per second).
    SAMPLE_RATE = 1000

    # Buffer size for each data update - big enough for good FFT, small enough to update the GUI smoothly.
    BUFFER_LEN = 1024

    # Default vibration limits per sensor to trigger alerts.
    DEFAULT_THRESHOLDS = [1.0, 2.0, 2.0, 3.0]
