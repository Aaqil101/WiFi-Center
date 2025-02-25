import platform
import re
import subprocess
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MasterWindow(QWidget):
    def __init__(self) -> None:
        """
        Initializes the MasterWindow class, setting up the UI components.

        This method sets the window title, size, and icon. It also initializes
        the layout and adds a label, a button to scan for Wi-Fi networks, and
        a list widget to display the available networks.
        Connects the scan button to the scan_wifi method to handle click events.
        """

        super().__init__()

        self.setWindowTitle("Wi-Fi Center")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon("assets/master_icon.png"))

        layout = QVBoxLayout()

        self.label = QLabel("Click 'Scan' to find available Wi-Fi networks")
        layout.addWidget(self.label)

        self.scan_button = QPushButton("Scan Wi-Fi")
        self.scan_button.clicked.connect(self.scan_wifi)
        layout.addWidget(self.scan_button)

        self.wifi_list = QListWidget()
        layout.addWidget(self.wifi_list)

        self.setLayout(layout)

    def get_os(self):
        os_name = platform.system()
        if os_name == "Windows":
            return "Windows"
        elif os_name == "Darwin":
            return "macOS"
        elif os_name == "Linux":
            return "Linux"
        else:
            return "Unknown OS"

    def scan_wifi(self):
        os_type = self.get_os()
        wifi_networks = []

        try:
            if os_type == "Windows":
                wifi_networks = self.get_wifi_windows()
            elif os_type == "macOS":
                wifi_networks = self.get_wifi_macos()
            elif os_type == "Linux":
                wifi_networks = self.get_wifi_linux()
            else:
                self.label.setText("Unsupported OS")
                return

            self.wifi_list.clear()
            if wifi_networks:
                self.wifi_list.addItems(wifi_networks)
            else:
                self.wifi_list.addItem("No Wi-Fi networks found")

        except Exception as e:
            self.wifi_list.addItem(f"Error: {e}")

    def get_wifi_windows(self):
        command = "netsh wlan show networks mode=bssid"
        output = subprocess.check_output(command, shell=True, encoding="utf-8")
        networks = re.findall(r"SSID \d+ : (.+)", output)
        return networks

    def get_wifi_macos(self):
        command = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s"
        output = subprocess.check_output(command, shell=True, encoding="utf-8")
        networks = re.findall(r"^([\w\-\s]+)", output, re.MULTILINE)
        return [
            ssid.strip() for ssid in networks if ssid.strip() and "SSID" not in ssid
        ]

    def get_wifi_linux(self):
        command = "nmcli -t -f SSID dev wifi"
        output = subprocess.check_output(command, shell=True, encoding="utf-8")
        return output.strip().split("\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec())
