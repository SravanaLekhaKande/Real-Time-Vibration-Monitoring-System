import sys
from PyQt5.QtWidgets import QApplication
from gui import VibrationMonitorGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VibrationMonitorGUI()
    window.show()
    sys.exit(app.exec_())
