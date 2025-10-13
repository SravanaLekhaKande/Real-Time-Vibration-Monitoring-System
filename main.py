"""
Main entry point for the Real Time Vibration Monitoring System GUI application.

This script initializes the PyQt application and launches the main window.
It creates a QApplication instance which manages the event loop for user
interaction. The VibrationMonitorGUI window is created and shown, and the
application enters its main event loop, waiting for events such as button
clicks or any uuser actions.

When the GUI is closed, the application exits cleanly.
"""
import sys
from PyQt5.QtWidgets import QApplication
from gui import VibrationMonitorGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VibrationMonitorGUI()
    window.show()
    sys.exit(app.exec_())
