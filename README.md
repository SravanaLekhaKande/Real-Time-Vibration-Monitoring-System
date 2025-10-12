# Real-Time Vibration Monitoring System

This Python application simulates four accelerometer sensors and performs real-time vibration monitoring. It displays live waveforms and FFTs, calculates RMS and peak values, and provides user-configurable threshold alerts through a clean PyQt5 GUI.

## Background
This project simulates data from four accelerometers mounted on a motor housing in Archer's propulsion test stand. The goal is to enable real-time vibration monitoring during endurance testing, assisting early fault detection and system health assessment.

## Features

- Simulates 4 accelerometer data streams with multi-frequency sine waves and noise
- Real-time waveform and frequency spectrum (FFT) visualization for each sensor
- RMS and peak vibration intensity calculation
- Threshold-based alerting with live panel status updates
- Threaded design to maintain smooth, responsive GUI performance

## Design & Architecture
- Modular design separating data simulation, signal processing, and GUI visualization layers
- Use of PyQt5 for GUI with threaded real-time updates
- Signal processing includes RMS and FFT for frequency analysis
- Threshold alerting implemented with user-configurable limits and visual feedback
  
## Installation

1. Clone this repo:
    ```
    git clone https://github.com/SravanaLekhaKande/Real-Time-Vibration-Monitoring-System.git
    ```

2. Create a Python virtual environment and activate it:
    ```
    python -m venv venv
    source venv/bin/activate # On iOS
    venv\Scripts\activate  # On Windows
    ```
    
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
    
## Usage

Run the main application script:
```
python main.py
```

Interact with the GUI to view sensor data, FFT, and configure alert thresholds.

## Evaluation Focus

- Clean, maintainable code organization prioritizing clarity over complexity
- Simple and effective GUI design using PyQt5
- Real-time performance with threaded data simulation and processing
- Practical signal processing approach balancing performance and demonstration

## Scope & Limitations

- Signals are simulated and not sourced from physical hardware
- Designed as a case study project scoped for 7-8 hours of development time
- Focused on demonstrating approach and engineering judgment rather than full production readiness

## Future Improvements

- Integration with actual hardware accelerometers for live data acquisition
- Addition of advanced algorithms for anomaly detection and classification
- Enhanced GUI customization and logging/data export features
- Expanded alerting with notifications and historical trends

## Notes

- This project was developed as a case study to demonstrate modular design, signal processing basics, threading with PyQt5, and real-time data visualization.
- Signals are simulated and do not come from actual hardware sensors.

## AI Usage

Assisted by AI tools for Python code suggestions and documentation.

