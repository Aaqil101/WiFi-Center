# Built-in Modules
import re
import time
from pathlib import Path
from typing import Any, Dict, Tuple

# PyWiFi & PyQt6 Modules
import pywifi
from PyQt6.QtCore import QTimer
from pywifi import const

# Helpers Modules
from helpers import (
    get_and_apply_styles,
    hide_output_box_with_animation,
    processing,
    show_output_box_with_animation,
)


# Add this class to your project
class WiFiConnectionManager:
    def __init__(self, window):
        """
        Initialize the WiFi Connection Manager

        Args:
            window: Reference to the main window
        """
        self.window = window
        self.wifi = pywifi.PyWiFi()
        try:
            self.iface = self.wifi.interfaces()[0]  # Get the first wireless interface
        except IndexError:
            self._show_error_message("No wireless interface found.")

        self.current_ssid = None
        self.password = None

    def scan_networks(self):
        """Scan for available Wi-Fi networks"""
        self.iface.scan()
        time.sleep(2)  # Wait for scan to complete
        return self.iface.scan_results()

    def is_valid_wifi_name(self, name: str) -> bool:
        """Check if the Wi-Fi name is valid"""
        # Wi-Fi SSID can be up to 32 characters
        return bool(name) and len(name) <= 32

    def is_network_available(self, target_ssid: str) -> bool:
        """Check if the specified network is available in scan results"""
        networks = self.scan_networks()
        available_ssids = [network.ssid for network in networks]

        if target_ssid in available_ssids:
            return True
        return False

    def parse_connection_command(self, command: str) -> Dict[str, Any]:
        """Parse connect command in format c=WIFINAME or connect=WIFINAME"""
        connect_match = re.match(r"^(?:c|connect)=(.+)$", command.strip())
        if connect_match:
            ssid = connect_match.group(1)
            if not self.is_valid_wifi_name(ssid):
                return {"status": "error", "message": "Invalid Wi-Fi name"}
            self.current_ssid = ssid
            return {"status": "ssid_set", "ssid": ssid}
        return {"status": "not_connect_command"}

    def parse_password_command(self, command: str) -> Dict[str, Any]:
        """Parse password command in format p=PASSWORD or password=PASSWORD"""
        password_match = re.match(r"^(?:p|password)=(.+)$", command.strip())
        if password_match:
            if not self.current_ssid:
                return {
                    "status": "error",
                    "message": "Please specify a Wi-Fi network first using c=WIFINAME",
                }
            self.password = password_match.group(1)
            return {"status": "password_set", "password": self.password}
        return {"status": "not_password_command"}

    def connect_to_network(self) -> Dict[str, str]:
        """Connect to the specified Wi-Fi network"""
        if not self.current_ssid:
            return {"status": "error", "message": "No Wi-Fi network specified"}

        # Check if network is available
        if not self.is_network_available(self.current_ssid):
            return {
                "status": "error",
                "message": f"Network '{self.current_ssid}' not found",
            }

        profile = pywifi.Profile()
        profile.ssid = self.current_ssid

        # If password is provided, configure security
        if self.password:
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_WPA2PSK)
            profile.cipher = const.CIPHER_TYPE_CCMP
            profile.key = self.password

        # Remove all existing profiles
        self.iface.remove_all_network_profiles()

        # Add new profile
        profile_added = self.iface.add_network_profile(profile)

        # Connect
        self.iface.connect(profile_added)

        # Wait for connection
        connection_timeout = 10  # seconds
        start_time = time.time()

        while time.time() - start_time < connection_timeout:
            status = self.iface.status()
            if status == const.IFACE_CONNECTED:
                return {
                    "status": "success",
                    "message": f"Successfully connected to {self.current_ssid}",
                }
            time.sleep(0.5)

        return {
            "status": "error",
            "message": f"Failed to connect to {self.current_ssid}. Check your password or network availability.",
        }

    def process_wifi_command(self, command: str) -> Tuple[bool, str]:
        """
        Process Wi-Fi related commands

        Args:
            command (str): User input command

        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        # Try connect command
        connect_result = self.parse_connection_command(command)
        if connect_result["status"] != "not_connect_command":
            if connect_result["status"] == "error":
                return False, connect_result["message"]
            return (
                True,
                f"Wi-Fi network set to: {self.current_ssid}. If password required, use p=PASSWORD",
            )

        # Try password command
        password_result = self.parse_password_command(command)
        if password_result["status"] != "not_password_command":
            if password_result["status"] == "error":
                return False, password_result["message"]

            # Attempt to connect now that we have both SSID and password
            connection_result = self.connect_to_network()
            return (
                connection_result["status"] == "success",
                connection_result["message"],
            )

        # Not a Wi-Fi related command
        return False, "not_wifi_command"

    def _show_error_message(self, message: str) -> None:
        """Display error message using the window's output box"""

        processing(self.window, begin=True)
        get_and_apply_styles(
            script_file=Path(__file__).parent,
            set_content_funcs={
                "output_box_failure.qss": self.window.output_box.setStyleSheet
            },
        )
        self.window.output_box.setPlainText(f"❌ {message}")

        # Show the output box with animation
        show_output_box_with_animation(self.window)

        # Hide the output box after 1.5 seconds and then enable the command bar
        QTimer.singleShot(1500, lambda: hide_output_box_with_animation(self.window))

        # Enable the command bar after the hide animation is complete (1800ms total)
        QTimer.singleShot(1800, lambda: processing(self.window, end=True))

    def _show_success_message(self, message: str) -> None:
        """Display success message using the window's output box"""

        processing(self.window, begin=True)
        get_and_apply_styles(
            script_file=Path(__file__).parent,
            set_content_funcs={
                "output_box_success.qss": self.window.output_box.setStyleSheet
            },
        )
        self.window.output_box.setPlainText(f"✅ {message}")

        # Show the output box with animation
        show_output_box_with_animation(self.window)

        # Hide the output box after 1.5 seconds and then enable the command bar
        QTimer.singleShot(1500, lambda: hide_output_box_with_animation(self.window))

        # Enable the command bar after the hide animation is complete (1800ms total)
        QTimer.singleShot(1800, lambda: processing(self.window, end=True))
