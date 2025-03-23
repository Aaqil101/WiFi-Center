#!/usr/bin/env python3
# wifi_scanner.py - Background script to scan for Wi-Fi networks with system tray icon and PyQt6 GUI

import datetime
import io
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Literal, Set

# PyWiFi Modules
try:
    from pywifi import PyWiFi, const, iface
except ImportError:
    print("Error: pywifi module not found. Please install with 'pip install pywifi'")
    sys.exit(1)

# PyQt6 for GUI
try:
    from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QAction, QIcon, QImage, QPixmap
    from PyQt6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMenu,
        QPushButton,
        QSystemTrayIcon,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("Error: PyQt6 modules not found. Please install with 'pip install PyQt6'")
    sys.exit(1)

# Constants
WIFI_DATA_FILE = Path(__file__).parent / "wifi_data.json"
SCAN_INTERVAL = 2  # seconds between scans
running = True
last_scan_time = None
log_messages = []
MAX_LOG_MESSAGES = 100

# For Windows console hiding
if os.name == "nt":
    import ctypes

    console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    # Hide the console window initially
    ctypes.windll.user32.ShowWindow(console_hwnd, 0)


# Signal class for cross-thread communication
class Signals(QObject):
    update_log = pyqtSignal(str)
    update_scan_time = pyqtSignal(str)


signals = Signals()


def log(message):
    """Log a message to console and emit signal for GUI."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)

    # Add to log messages
    log_messages.append(log_entry)
    if len(log_messages) > MAX_LOG_MESSAGES:
        log_messages.pop(0)

    # Emit signal for GUI update
    signals.update_log.emit(log_entry)


def get_wifi_interface() -> iface.Interface:
    """Get the first available WiFi interface."""
    try:
        wifi = PyWiFi()
        if wifi.interfaces():
            return wifi.interfaces()[0]
        else:
            log("No WiFi interfaces found")
            sys.exit(1)
    except Exception as e:
        log(f"Error initializing WiFi interface: {e}")
        sys.exit(1)


def scan_wifi_networks() -> List[Dict]:
    """
    Scan for available Wi-Fi networks.

    Returns:
        A list of dictionaries containing network information
    """
    global last_scan_time

    interface = get_wifi_interface()

    # Get saved profiles (connections)
    saved_profiles: Set[str] = {
        profile.ssid for profile in interface.network_profiles()
    }

    # Trigger scan
    interface.scan()

    # Wait for scan to complete
    time.sleep(1.0)

    # Get scan results
    scan_results = interface.scan_results()

    # Process scan results
    networks_dict: Dict[str, Dict] = {}

    for result in scan_results:
        ssid: str = result.ssid
        if not ssid:  # Skip networks with empty SSIDs
            continue

        # Convert signal strength (dBm) to percentage (0-100%)
        signal_strength: int = min(max(0, (result.signal + 100) * 2), 100)
        signal_percent = int(signal_strength)

        # Check if authentication is required
        requires_login: bool = (
            result.akm[0] != const.AKM_TYPE_NONE and ssid not in saved_profiles
        )

        # Keep only the strongest signal for each SSID
        if (
            ssid not in networks_dict
            or signal_percent > networks_dict[ssid]["strength"]
        ):
            current_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(time.time())
            )
            networks_dict[ssid] = {
                "ssid": ssid,
                "strength": signal_percent,
                "requires_login": requires_login,
                "last_seen": current_time,
            }

    # Update last scan time
    last_scan_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    signals.update_scan_time.emit(last_scan_time)

    # Convert to list and sort
    result = sorted(networks_dict.values(), key=lambda x: x["strength"], reverse=True)

    return result[:6]  # Return top 6 networks by signal strength


def save_to_json(networks: List[Dict]) -> None:
    """Save network data to JSON file."""
    try:
        with open(WIFI_DATA_FILE, "w") as f:
            json.dump(networks, f, indent=2)
    except Exception as e:
        log(f"Error saving to {WIFI_DATA_FILE}: {e}")


def create_tray_icon():
    """Generate a WiFi icon for the system tray."""
    from PIL import Image, ImageDraw

    # Create an image with a transparent background
    width = 64
    height = 64
    color1 = (255, 255, 255)  # White

    # Create a new image with a transparent background
    image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
    dc = ImageDraw.Draw(image)

    # Draw a simple WiFi icon
    dc.arc([10, 10, 54, 54], 0, 180, fill=color1, width=3)
    dc.arc([20, 20, 44, 44], 0, 180, fill=color1, width=3)
    dc.arc([30, 30, 34, 34], 0, 180, fill=color1, width=3)

    # Save to a byte array
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")

    return img_byte_arr.getvalue()


def scanner_process():
    """Main scanning process that runs in the background."""
    global running

    log("WiFi scanner started")

    try:
        while running:
            networks = scan_wifi_networks()
            save_to_json(networks)
            log(f"Scanned {len(networks)} networks")
            time.sleep(SCAN_INTERVAL)
    except Exception as e:
        log(f"Error in scanner process: {e}")


class ConsoleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("WiFi Scanner Console")
        self.setMinimumSize(700, 500)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Last scan time label
        self.scan_time_label = QLabel("Last scan: Not scanned yet")
        self.scan_time_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        self.scan_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.scan_time_label)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        main_layout.addWidget(self.log_display)

        # Button area
        button_layout = QHBoxLayout()

        # Clear log button
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)

        # Force scan button
        self.scan_button = QPushButton("Force Scan Now")
        self.scan_button.clicked.connect(self.force_scan)
        button_layout.addWidget(self.scan_button)

        main_layout.addLayout(button_layout)

        # Connect signals
        signals.update_log.connect(self.add_log)
        signals.update_scan_time.connect(self.update_scan_time)

        # Load existing logs
        for msg in log_messages:
            self.log_display.append(msg)

        # Update scan time if available
        if last_scan_time:
            self.update_scan_time(last_scan_time)

    def add_log(self, message):
        """Add a log message to the display."""
        self.log_display.append(message)
        # Scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_scan_time(self, time_str):
        """Update the last scan time display."""
        self.scan_time_label.setText(f"Last scan: {time_str}")

    def clear_log(self):
        """Clear the log display."""
        self.log_display.clear()
        global log_messages
        log_messages = []
        log("Log cleared")

    def force_scan(self):
        """Force an immediate scan."""
        log("Manual scan initiated")
        # Run in a separate thread to avoid freezing UI
        scan_thread = threading.Thread(target=self.perform_scan)
        scan_thread.daemon = True
        scan_thread.start()

    def perform_scan(self):
        """Perform the actual scan operation."""
        networks = scan_wifi_networks()
        save_to_json(networks)
        log(f"Manual scan complete - found {len(networks)} networks")

    def closeEvent(self, event):
        """Handle window close event."""
        # Just hide the window instead of closing the application
        event.ignore()
        self.hide()


class WiFiScannerApp(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.setQuitOnLastWindowClosed(False)

        # Create console window
        self.console = ConsoleWindow()

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Create tray icon
        icon_data = create_tray_icon()
        pixmap = QPixmap()
        pixmap.loadFromData(icon_data)
        self.tray_icon.setIcon(QIcon(pixmap))

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show Console", self)
        show_action.triggered.connect(self.show_console)
        tray_menu.addAction(show_action)

        view_data_action = QAction("View WiFi Data", self)
        view_data_action.triggered.connect(self.view_data)
        tray_menu.addAction(view_data_action)

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)

        # Show the tray icon
        self.tray_icon.show()

        # Start scanner thread
        self.scanner_thread = threading.Thread(target=scanner_process)
        self.scanner_thread.daemon = True
        self.scanner_thread.start()

    def show_console(self):
        """Show the console window."""
        self.console.show()
        self.console.raise_()
        self.console.activateWindow()

    def view_data(self):
        """Open the data file."""
        if os.name == "nt":
            os.startfile(WIFI_DATA_FILE)
        else:
            os.system(f"open {WIFI_DATA_FILE}")

    def tray_activated(self, reason):
        """Handle tray icon activation (double-click)."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_console()

    def quit_app(self):
        """Quit the application."""
        global running
        running = False
        # Allow time for the scanner thread to terminate
        time.sleep(0.5)
        self.quit()


def main():
    """Main function to run the Wi-Fi scanner with PyQt6 GUI."""

    # Create Qt application
    app = WiFiScannerApp(sys.argv)

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
