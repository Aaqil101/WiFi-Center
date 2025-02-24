# Import Packages/Modules
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow


class MasterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Fi Center")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon("assets/master_icon.png"))


def master():
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    master()
