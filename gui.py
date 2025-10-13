"""
VibrationMonitorGUI: Real-Time Vibration Monitoring System GUI

This module defines the main GUI for the vibration monitoring system. It
displays waveform and FFT plots for multiple accelerometer sensors, shows
real-time RMS and peak vibration values, and alerts the user if vibration
limits are exceeded. Users can set custom alert thresholds for each sensor
and pause/resume data streaming.

The GUI runs the accelerometer simulation in a separate thread, updates
plots asynchronously, and manages UI components for both grid and
individual sensor views.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDoubleSpinBox, QGroupBox, QGridLayout,
    QTabWidget, QStatusBar, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from simulation import AccelerometerSimulator
from signal_processing import compute_fft, compute_rms
from config import Config

class SensorPanel(QWidget):
    def __init__(self, sensor_idx, buffer_len, sample_rate, is_compact=False, parent=None):
        super().__init__(parent)
        # Basic configuration of the sensor panel display state and data buffers
        self.sensor_idx = sensor_idx
        self.buffer_len = buffer_len
        self.sample_rate = sample_rate
        self.is_compact = is_compact
        self.data = None
        self.init_ui() # Initiating the widget UI

    def init_ui(self):
        # Layout Creation
        layout = QVBoxLayout()
        layout.setSpacing(6 if self.is_compact else 12)
        layout.setContentsMargins(6, 6, 6, 6)

        # Title label showing sensor numbers
        title_font_size = 14 if self.is_compact else 12
        self.title_label = QLabel(f"Sensor {self.sensor_idx + 1} - Accelerometer")
        self.title_label.setFont(QFont("Arial", title_font_size, QFont.Bold))
        self.title_label.setStyleSheet("color: navy; margin-bottom: 8px;")
        layout.addWidget(self.title_label, alignment=Qt.AlignHCenter)

        # Setup matplotlib figure and canvas for waveform and FFT plots
        fig_width, fig_height = (6.2, 3.0) if self.is_compact else (8, 25)
        self.figure = Figure(figsize=(fig_width, fig_height))
        self.canvas = FigureCanvas(self.figure)

        # Control canvas height for consistent UI appearance
        canvas_min_height = 1200 if self.is_compact else 450
        canvas_max_height = canvas_min_height + 30
        self.canvas.setMinimumHeight(canvas_min_height)
        self.canvas.setMaximumHeight(canvas_max_height)
        self.ax1 = self.figure.add_subplot(211)
        self.ax2 = self.figure.add_subplot(212)
        layout.addWidget(self.canvas)

        #  UI widget initialization for RMS, Peak, Status labels
        if self.is_compact:      
            label_font_size = 20
            value_font_size = 20
            fixed_width_rms = 120
            fixed_width_peak = 120
            fixed_width_status = 150
            rms_padding = 1
        else:
            label_font_size = 12
            value_font_size = 12
            fixed_width_rms = 80
            fixed_width_peak = 80
            fixed_width_status = 120
            rms_padding = 3

        label_title_font = QFont("Arial", label_font_size, QFont.Bold)
        val_font = QFont("Arial", value_font_size, QFont.Bold)

        # RMS
        self.rms_label_title = QLabel("RMS:")
        self.rms_label_title.setFont(label_title_font)
        self.rms_label_title.setStyleSheet("color: black;")
        self.rms_label_val = QLabel("0.00")
        self.rms_label_val.setFont(val_font)
        self.rms_label_val.setAlignment(Qt.AlignCenter)
        self.rms_label_val.setFixedHeight(50)
        self.rms_label_val.setFixedWidth(fixed_width_rms)
        self.rms_label_val.setStyleSheet("background-color: lightgrey; border-radius: 5px; padding: 2px;")
        rms_layout = QHBoxLayout()
        rms_layout.addWidget(self.rms_label_title)
        rms_layout.addWidget(self.rms_label_val)
        rms_layout.addStretch()

        # Peak
        self.peak_label_title = QLabel("Peak:")
        self.peak_label_title.setFont(label_title_font)
        self.peak_label_title.setStyleSheet("color: black;")
        self.peak_label_val = QLabel("0.00")
        self.peak_label_val.setFont(val_font)
        self.peak_label_val.setAlignment(Qt.AlignCenter)
        self.peak_label_val.setFixedHeight(50)
        self.peak_label_val.setFixedWidth(fixed_width_peak)
        self.peak_label_val.setStyleSheet("background-color: lightgrey; border-radius: 4px; padding: 2px;")
        peak_layout = QHBoxLayout()
        peak_layout.addWidget(self.peak_label_title)
        peak_layout.addWidget(self.peak_label_val)
        peak_layout.addStretch()

        # Status
        self.status_label_title = QLabel("Status:")
        self.status_label_title.setFont(label_title_font)
        self.status_label_title.setStyleSheet("color: black;")
        self.status_label_val = QLabel("OK")
        self.status_label_val.setFont(val_font)
        self.status_label_val.setAlignment(Qt.AlignCenter)
        self.status_label_val.setFixedHeight(50)
        self.status_label_val.setFixedWidth(fixed_width_status)
        self.status_label_val.setStyleSheet("background-color: lightgreen; border-radius: 3px; padding: 2px;")
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label_title)
        status_layout.addWidget(self.status_label_val)
        status_layout.addStretch()

        info_layout = QHBoxLayout()
        info_layout.addLayout(rms_layout)
        info_layout.addSpacing(10 if self.is_compact else 20)
        info_layout.addLayout(peak_layout)
        info_layout.addSpacing(10 if self.is_compact else 20)
        info_layout.addLayout(status_layout)
        info_layout.addStretch()

        layout.addLayout(info_layout)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    def update_plot(self, data, threshold):
        # Update waveform and FFT based on new live data samples
        self.data = data
        t = range(self.buffer_len)
        self.ax1.clear()
        self.ax2.clear()

        # Plot waveform
        self.ax1.plot(t, data, lw=2, color='royalblue')
        self.ax1.set_title("Waveform", fontsize=25 if self.is_compact else 15, loc='left', fontweight='bold')
        self.ax1.set_xlabel("Sample Index", fontsize=16 if self.is_compact else 13)
        self.ax1.set_ylabel("Amplitude", fontsize=16 if self.is_compact else 13)
        if not self.is_compact:  
            self.figure.tight_layout()

        # Compute and update RMS and Peak labels
        rms = compute_rms(data)
        peak = max(abs(data))
        self.rms_label_val.setText(f"{rms:.2f}")
        self.peak_label_val.setText(f"{peak:.2f}")
        
        self.update_status(rms, threshold)

        # Plot FFT spectrum
        freqs, vals = compute_fft(data, self.sample_rate)
        self.ax2.plot(freqs, vals, lw=1.5, color='darkorange')
        self.ax2.set_xlim(0, self.sample_rate / 2)
        self.ax2.set_title("FFT Spectrum", fontsize=25 if self.is_compact else 15, loc='left', fontweight='bold')
        self.ax2.set_xlabel("Frequency (Hz)", fontsize=16 if self.is_compact else 13)
        self.ax2.set_ylabel("Magnitude", fontsize=16 if self.is_compact else 13)
        if not self.is_compact:  
            self.figure.tight_layout()
        self.canvas.draw_idle()

    def update_status(self, rms, threshold):
        # Check if vibration RMS value exceeds the alert threshold
        if rms > threshold:
            # Show alert text and style with red on pink background to grab attention
            self.status_label_val.setText("ALERT")
            self.status_label_val.setStyleSheet(
                "background-color: pink; border-radius: 3px; padding: 2px; color: red; font-weight: bold;"
            )
        else:
            # Normal state with green background and "OK" to indicate system is fine
            self.status_label_val.setText("OK")
            self.status_label_val.setStyleSheet(
                "background-color: lightgreen; border-radius: 3px; padding: 2px; color: green; font-weight: normal;"
            )

class VibrationMonitorGUI(QWidget):
    def __init__(self):
        super().__init__()
        # Set window title and get config constants
        self.setWindowTitle("Real-Time Vibration Monitoring System")
        self.sensor_count = Config.SENSOR_COUNT
        self.sample_rate = Config.SAMPLE_RATE
        self.buffer_len = Config.BUFFER_LEN
        self.thresholds = Config.DEFAULT_THRESHOLDS[:]
        self.init_ui()

        # Setup a thread and worker to simulate accelerometer data in background
        self.worker_thread = QThread()
        self.worker = AccelerometerSimulator(
            sensor_count=self.sensor_count,
            freq=self.sample_rate,
            buffer_len=self.buffer_len
        )
        self.worker.moveToThread(self.worker_thread)

        # Connect signals for starting, receiving data, finishing and cleanup
        self.worker_thread.started.connect(self.worker.run)
        self.worker.data_ready.connect(self.handle_new_data)  
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # Start the data simulation thread
        self.worker_thread.start()

        # Maximize the window on startup
        self.showMaximized()

    def create_single_sensor_threshold_widget(self, sensor_idx):
        # Create widget for adjusting alert threshold for an individual sensor
        container = QWidget()
        layout = QHBoxLayout()
        sensor_label = QLabel(f"Threshold for Sensor {sensor_idx + 1}")
        sensor_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        spin = QDoubleSpinBox()
        spin.setDecimals(3)  
        spin.setMinimum(0.0)
        spin.setMaximum(10.0)
        spin.setSingleStep(0.5)
        spin.setValue(int(self.thresholds[sensor_idx]))
        spin.setToolTip(f"Set alert RMS threshold for Sensor {sensor_idx + 1}")
        spin.setFont(QFont("Arial", 12))
        spin.setFixedWidth(200)
        
        layout.addStretch()
        layout.addWidget(sensor_label)
        layout.addWidget(spin)
        layout.addStretch()
        container.setLayout(layout)
        return container, spin

    def init_ui(self):
        # Create the main UI layout
        self.setMinimumSize(900, 700)
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        tab_bar = self.tabs.tabBar()
        font = tab_bar.font()
        font.setPointSize(14)
        tab_bar.setFont(font)

        # Custom CSS for tabs
        tab_bar.setStyleSheet("""
            QTabBar::tab {
                min-width: 250px;
                height: 40px;
                padding-left: 15px;
                padding-right: 15px;
                font-weight: bold;
                background: lightgray;
                border: 1px solid gray;
                border-bottom-color: transparent;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                color: black;
                border: 2px solid #0078d7;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background: #d0eaff;
            }
        """)

        # List to hold all pause buttons for syncing text
        self.pause_buttons = []

        # Keep references for threshold spin boxes in both views for syncing
        self.grid_threshold_spins = []
        self.individual_threshold_spins = []

        # Grid tab - overview of all sensors in a grid layout
        grid_tab = QWidget()
        grid_layout = QVBoxLayout()
        grid = QGridLayout()
        grid.setSpacing(20)
        self.sensor_panels_grid = []
        for i in range(self.sensor_count):
            panel = SensorPanel(i, self.buffer_len, self.sample_rate, is_compact=False)
            panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.sensor_panels_grid.append(panel)
            grid.addWidget(panel, i // 2, i % 2)
        grid_layout.addLayout(grid)

        # Alert thresholds below the grid
        config_box = QGroupBox("Alert Thresholds (Hover for help)")
        config_box.setFont(QFont("Arial", 12, QFont.Bold))
        config_layout = QHBoxLayout()
        config_layout.setSpacing(12)

        #self.thresh_spins = []
        for i in range(self.sensor_count):
            box = QHBoxLayout()
            sensor_label = QLabel(f"Sensor {i + 1}")
            sensor_label.setFont(QFont("Arial", 12, QFont.Bold))
            sensor_label.setStyleSheet("margin-right: 2px;")
            sensor_label.setFixedWidth(200)

            spin = QDoubleSpinBox()
            spin.setDecimals(3)  
            spin.setMinimum(0.0)
            spin.setMaximum(10.0)
            spin.setSingleStep(0.5)
            spin.setValue(int(self.thresholds[i]))
            spin.setToolTip(f"Set alert RMS threshold for Sensor {i + 1}")
            spin.setFont(QFont("Arial", 14))
            spin.setFixedWidth(200)
            
            # Connect threshold  changes to handler
            spin.valueChanged.connect(lambda val, idx=i: self.threshold_changed(idx, val))
            box.addWidget(sensor_label)
            box.addWidget(spin)
            container = QWidget()
            container.setLayout(box)
            config_layout.addWidget(container)
            self.grid_threshold_spins.append(spin)
            #self.thresh_spins.append(spin)

        config_box.setLayout(config_layout)
        config_box.setStyleSheet("margin:10px;")
        grid_layout.addWidget(config_box)

        # Alert message label & pause button below grid
        self.msg_label = QLabel("")
        self.msg_label.setToolTip("Alert messages and warnings appear here")
        self.msg_label.setStyleSheet("color: red; font-size: 22px; font-weight: bold;")
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignCenter)

        # Pause button for grid tab
        pause_btn_grid = QPushButton("Pause")
        pause_btn_grid.setToolTip("Pause/Resume data streaming")
        pause_btn_grid.setFont(QFont("Arial", 13))
        pause_btn_grid.setFixedWidth(110)
        pause_btn_grid.clicked.connect(self.toggle_pause)
        self.pause_buttons.append(pause_btn_grid)
        
        # Bottom layout with alert message and pause button in grid tab
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.msg_label, stretch=3)
        bottom_layout.addStretch()
        bottom_layout.addWidget(pause_btn_grid, stretch=0)
        grid_layout.addLayout(bottom_layout)

        grid_tab.setLayout(grid_layout)
        self.tabs.addTab(grid_tab, "All Sensors")

        # Individual tabs for each sensor with bigger plots with threshold and pause button
        self.sensor_panels_individual = []
        for i in range(self.sensor_count):
            panel = SensorPanel(i, self.buffer_len, self.sample_rate, is_compact=True)
            single_panel_tab = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(panel, stretch=8)  # Give most space to plot

            # Threshold control for this sensor only
            box = QHBoxLayout()
            sensor_label = QLabel(f"Threshold for Sensor {i + 1}")
            sensor_label.setFont(QFont("Arial", 14, QFont.Bold))
            spin = QDoubleSpinBox()
            spin.setDecimals(3)  
            spin.setMinimum(0.0)
            spin.setMaximum(10.0)
            spin.setSingleStep(0.5)
            spin.setValue(int(self.thresholds[i]))
            spin.setToolTip(f"Set alert RMS threshold for Sensor {i + 1}")
            spin.setFont(QFont("Arial", 14))

            # connect signal to slot for threshold change
            spin.valueChanged.connect(lambda val, idx=i: self.threshold_changed(idx, val))
            
            spin.setFixedWidth(200)
            box.addStretch()
            box.addWidget(sensor_label)
            box.addWidget(spin)
            box.addStretch()
            threshold_widget = QWidget()
            threshold_widget.setLayout(box)
            layout.addWidget(threshold_widget, stretch=1)

            # Pause button for individual sensor tab
            pause_btn_individual = QPushButton("Pause")
            pause_btn_individual.setToolTip("Pause/Resume data streaming")
            pause_btn_individual.setFont(QFont("Arial", 13))
            pause_btn_individual.setFixedWidth(110)
            pause_btn_individual.clicked.connect(self.toggle_pause)
            self.pause_buttons.append(pause_btn_individual)

            pause_layout = QHBoxLayout()
            pause_layout.addStretch()
            pause_layout.addWidget(pause_btn_individual, stretch=0)
            pause_layout.addStretch()
            layout.addLayout(pause_layout)

            single_panel_tab.setLayout(layout)
            single_panel_tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            self.tabs.addTab(single_panel_tab, f"Sensor {i + 1}")
            self.sensor_panels_individual.append(panel)
            self.individual_threshold_spins.append(spin)

        main_layout.addWidget(self.tabs, stretch=1)
        self.setLayout(main_layout)
        self.paused = False


    def handle_new_data(self, signals):
        # Handle incoming new accelerometer data from the worker thread
        if self.paused:
            return   # Skip updating if paused
        alerts = []
        focused_sensors = []
        for idx in range(self.sensor_count):
            data = signals[idx]
            threshold = self.grid_threshold_spins[idx].value()
            self.sensor_panels_grid[idx].update_plot(data, threshold)
            self.sensor_panels_individual[idx].update_plot(data, threshold)
            self.update_sensor_status(idx)
            rms = compute_rms(data)
            if rms > threshold:
                focused_sensors.append(f"Sensor {idx + 1}")
                alerts.append(f"Sensor {idx + 1}: RMS {rms:.2f} > {threshold}")

        # Show alert message if any sensor exceeds threshold
        if alerts:
            focus_list = ", ".join(focused_sensors)
            message = (f"ALERT! Please focus on the following sensors:\n{focus_list}")
            self.msg_label.setText(message)
            self.msg_label.setStyleSheet("color: red; font-size: 24px;")
        else:
            self.msg_label.setText("System normal. No alerts.")
            self.msg_label.setStyleSheet("color: green; font-size: 24px;")

    def set_threshold(self, idx, val):
        # Set threshold value for sensor by index
        self.thresholds[idx] = float(val)

    def threshold_changed(self, sensor_index, new_value):
        # Update internal threshold array
        self.thresholds[sensor_index] = new_value

        # Sync the threshold values between grid and individual spin boxes without recursion
        if self.grid_threshold_spins and self.individual_threshold_spins:
            grid_spin = self.grid_threshold_spins[sensor_index]
            individual_spin = self.individual_threshold_spins[sensor_index]

            sender = self.sender()
            if sender == grid_spin and individual_spin.value() != new_value:
                individual_spin.blockSignals(True)
                individual_spin.setValue(new_value)
                individual_spin.blockSignals(False)
            elif sender == individual_spin and grid_spin.value() != new_value:
                grid_spin.blockSignals(True)
                grid_spin.setValue(new_value)
                grid_spin.blockSignals(False)

        # Update sensor status to reflect new threshold
        self.update_sensor_status(sensor_index)

    def update_sensor_status(self, sensor_index):
        # Update the status labels for sensor in both grid and individual panels
        grid_panel = self.sensor_panels_grid[sensor_index]
        individual_panel = self.sensor_panels_individual[sensor_index]

        try:
            rms_val_grid = float(grid_panel.rms_label_val.text())
        except ValueError:
            rms_val_grid = 0.0
        try:
            rms_val_individual = float(individual_panel.rms_label_val.text())
        except ValueError:
            rms_val_individual = 0.0

        current_rms = max(rms_val_grid, rms_val_individual)
        threshold = self.thresholds[sensor_index]

        grid_panel.update_status(current_rms, threshold)
        individual_panel.update_status(current_rms, threshold)

    def toggle_pause(self):
        # Toggle pause/resume state for data updates and change pause buttons text
        self.paused = not self.paused
        new_text = "Resume" if self.paused else "Pause"
        for btn in self.pause_buttons:
            btn.setText(new_text)

    def closeEvent(self, event):
        # When main window closes, stop worker and thread cleanly, then finish closing
        self.worker.stop()
        self.worker_thread.quit()
        self.worker_thread.wait()
        super().closeEvent(event)


