#!/usr/bin/env python3
# wifi_scanner.py - Background script to scan for Wi-Fi networks with system tray icon and PyQt6 GUI

# Build-in Modules
import datetime
import json
import os
import socket
import sys
import threading
import time
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, List, Set

# PyQt6 Modules
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeyEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollBar,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# PyWiFi Modules
from pywifi import PyWiFi, const, iface

# Scan Helpers Modules
from scan_helpers import Blur, get_and_apply_styles

# Constants
WIFI_DATA_FILE: Path = Path(__file__).parent.parent / "wifi_data.json"
SCAN_INTERVAL = 1
running = True
last_scan_time = None
log_messages: list = []
MAX_LOG_MESSAGES = 100

# For Windows console hiding
if os.name == "nt":
    import ctypes

    console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    # Hide the console window initially
    ctypes.windll.user32.ShowWindow(console_hwnd, 0)


# Single Instance Check
class SingleInstance:
    """Ensure only one instance of the application is running."""

    def __init__(self, port=50000) -> None:
        """
        Initialize single instance check using a socket.

        Args:
            port (int): Port to use for single instance check
        """
        self.port = port
        self.socket = None

    def already_running(self) -> bool:
        """
        Check if another instance is already running.

        Returns:
            bool: True if another instance is running, False otherwise
        """
        try:
            # Try to create a socket and bind to a specific port
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(("127.0.0.1", self.port))
            self.socket.listen(1)
            return False
        except socket.error:
            # Port is already in use, meaning another instance is running
            return True

    def __del__(self) -> None:
        """Close the socket when the object is deleted."""
        if hasattr(self, "socket") and self.socket:
            try:
                self.socket.close()
            except:
                pass


# Signal class for cross-thread communication
class Signals(QObject):
    update_log = pyqtSignal(str)
    update_scan_time = pyqtSignal(str)


signals = Signals()


def log(message) -> None:
    """Log a message to console and emit signal for GUI."""
    timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry: str = f"[{timestamp}] {message}"
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

    interface: iface.Interface = get_wifi_interface()

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
            current_time: str = time.strftime(
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
            json.dump(networks, f, indent=4)
    except Exception as e:
        log(f"Error saving to {WIFI_DATA_FILE}: {e}")


def scanner_process() -> None:
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
    def __init__(self) -> None:
        super().__init__()

        # Set window properties
        self.setWindowTitle("WiFi Scanner Console")
        self.setMinimumSize(650, 490)

        # Set window icon
        window_icon_path: Path = (
            Path(__file__).parent / "assets" / "wifi_scanner_window_icon.png"
        )
        self.setWindowIcon(QIcon(str(window_icon_path)))

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Last scan time label
        self.scan_time_label = QLabel("Last scan: Not scanned yet")
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

        get_and_apply_styles(
            script_file=__file__,
            set_content_funcs={
                "last_scan_time.qss": self.scan_time_label.setStyleSheet,
                "clear_button.qss": self.clear_button.setStyleSheet,
                "force_scan_button.qss": self.scan_button.setStyleSheet,
                "log_display.qss": self.log_display.setStyleSheet,
            },
        )

        # Apply window style
        self.apply_window_style()

        # Load existing logs
        for msg in log_messages:
            self.log_display.append(msg)

        # Update scan time if available
        if last_scan_time:
            self.update_scan_time(last_scan_time)

    @lru_cache(maxsize=1)
    def is_windows_11(self) -> bool:
        """
        Check if the system is running Windows 11.

        Returns:
            bool: True if Windows 11 (build >= 22000), False otherwise
        """
        windows_build: int = sys.getwindowsversion().build
        return windows_build >= 22000

    def apply_window_style(self) -> None:
        if self.is_windows_11():
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            get_and_apply_styles(
                script_file=__file__,
                set_content_funcs={
                    "win11.qss": self.setStyleSheet,
                },
            )
            Blur(self.winId(), DarkMode=True)
        else:
            get_and_apply_styles(
                script_file=__file__,
                set_content_funcs={
                    "win10.qss": self.setStyleSheet,
                },
            )

    def add_log(self, message) -> None:
        """Add a log message to the display."""
        self.log_display.append(message)
        # Scroll to bottom
        scrollbar: QScrollBar | None = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_scan_time(self, time_str) -> None:
        """Update the last scan time display."""
        self.scan_time_label.setText(f"Last scan: {time_str}")

    def clear_log(self) -> None:
        """Clear the log display."""
        self.log_display.clear()
        global log_messages
        log_messages = []
        log("Log cleared")

    def force_scan(self) -> None:
        """Force an immediate scan."""
        log("Manual scan initiated")
        # Run in a separate thread to avoid freezing UI
        scan_thread = threading.Thread(target=self.perform_scan)
        scan_thread.daemon = True
        scan_thread.start()

    def perform_scan(self) -> None:
        """Perform the actual scan operation."""
        networks = scan_wifi_networks()
        save_to_json(networks)
        log(f"Manual scan complete - found {len(networks)} networks")

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Just hide the window instead of closing the application
        event.ignore()
        self.hide()


class WiFiScannerApp(QApplication):
    def __init__(self, args) -> None:
        super().__init__(args)

        self.setQuitOnLastWindowClosed(False)

        # Create console window
        self.console = ConsoleWindow()

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("WiFi Scanner")

        # Create tray icon
        tray_icon_path: Path = (
            Path(__file__).parent / "assets" / "wifi_scanner_tray_icon.png"
        )
        with open(tray_icon_path, "rb") as f:
            icon_data: bytes = f.read()
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

    def show_console(self) -> None:
        """Show the console window."""
        self.console.show()
        self.console.raise_()
        self.console.activateWindow()

    def view_data(self) -> None:
        """Open the data file."""
        if os.name == "nt":
            os.startfile(WIFI_DATA_FILE)
        else:
            os.system(f"open {WIFI_DATA_FILE}")

    def tray_activated(self, reason) -> None:
        """Handle tray icon activation (double-click)."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_console()

    def quit_app(self) -> None:
        """Quit the application."""
        global running
        running = False
        # Allow time for the scanner thread to terminate
        time.sleep(0.5)
        self.quit()


def main():
    """Main function to run the Wi-Fi scanner with PyQt6 GUI."""
    # Check for single instance
    single_instance = SingleInstance()

    if single_instance.already_running():
        # Show message box
        app = QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "WiFi Scanner",
            "Another instance of WiFi Scanner is already running.",
            QMessageBox.StandardButton.Ok,
        )
        sys.exit(1)

    # Create Qt application
    app = WiFiScannerApp(sys.argv)

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
