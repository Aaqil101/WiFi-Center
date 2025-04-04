# Build-in Modules
import re
import sys
import time
from argparse import Namespace
from functools import lru_cache
from pathlib import Path

# PyWiFi Modules
import pywifi

# Connect Helpers Modules
from connect_helpers import Blur, center_on_screen, get_and_apply_styles

# PyQt6 Modules
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class PasswordDialog(QDialog):
    def __init__(self, ssid, parent=None) -> None:
        super().__init__(parent)
        self.ssid = ssid
        self.password = None
        self.init_ui()

    def init_ui(self) -> None:
        # Set window properties
        self.setWindowTitle("Connect to Wi-Fi Network")
        self.setFixedSize(400, 250)

        icon_path: Path = Path(__file__).parent / "assets" / "connect_to_wifi_icon.png"

        self.setWindowIcon(QIcon(str(icon_path)))

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Network name section
        wifi_label = QLabel(f"Enter the password for: {self.ssid}")

        # Password section
        password_label = QLabel("Security key:")
        password_label.adjustSize()

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(30)

        # Show password checkbox
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password_visibility)

        # Horizontal line separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(32)
        self.cancel_button.setMinimumWidth(80)
        self.cancel_button.clicked.connect(self.reject)

        self.next_button = QPushButton("Connect")
        self.next_button.setMinimumHeight(32)
        self.next_button.setMinimumWidth(80)
        self.next_button.clicked.connect(self.accept_password)
        self.next_button.setDefault(True)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.next_button)

        # Apply styles
        get_and_apply_styles(
            script_file=__file__,
            set_content_funcs={
                "cancel_button.qss": self.cancel_button.setStyleSheet,
                "next_button.qss": self.next_button.setStyleSheet,
                "password_label.qss": password_label.setStyleSheet,
                "wifi_label.qss": wifi_label.setStyleSheet,
                "password_edit.qss": self.password_edit.setStyleSheet,
                "show_password.qss": self.show_password.setStyleSheet,
            },
        )

        # Add widgets to main layout
        main_layout.addWidget(wifi_label)
        main_layout.addWidget(password_label)
        main_layout.addWidget(self.password_edit)
        main_layout.addWidget(self.show_password)
        main_layout.addStretch()
        main_layout.addWidget(line)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.apply_window_style()
        center_on_screen(self)

    def toggle_password_visibility(self, checked) -> None:
        """
        Toggles the visibility of the password in the password edit field.

        :param checked: True to show the password, False to hide it
        :type checked: bool
        """
        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def accept_password(self) -> None:
        """
        Called when the user clicks the "Connect" button. Retrieves the password
        from the password edit field, and then accepts the dialog, which will
        cause the entered password to be returned to the caller of
        `PasswordDialog.exec()`.
        """
        self.password: str = self.password_edit.text()
        self.accept()

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
        """
        Applies the appropriate window style based on the Windows version.

        This function checks the Windows build version to determine if the system
        is running Windows 11 or an earlier version. Depending on the version, it
        applies the corresponding stylesheets and settings to the window and its
        components.

        On Windows 11:
            - Sets the window to have a translucent background.
            - Applies styles from 'win11.qss'.
            - Enables blur effects on the window.

        On Windows 10 or earlier:
            - Applies styles from 'win10.qss'.
        """
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


class WiFiConnector:
    def __init__(self) -> None:
        self.wifi = pywifi.PyWiFi()
        try:
            self.iface = self.wifi.interfaces()[0]  # Get the first wireless interface
        except IndexError:
            print("Error: No wireless interface found.")
            sys.exit(1)

        self.current_ssid = None
        self.password = None
        self.requires_password = False

        # Initialize QApplication if not already initialized
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

    def scan_networks(self):
        """Scan for available Wi-Fi networks"""
        self.iface.scan()
        time.sleep(2)  # Wait for scan to complete
        return self.iface.scan_results()

    def is_valid_wifi_name(self, name) -> bool:
        """Check if the Wi-Fi name is valid"""
        # Wi-Fi SSID can be up to 32 characters
        return bool(name) and len(name) <= 32

    def get_network_info(self, target_ssid):
        """Get information about a specific network"""
        networks = self.scan_networks()

        for network in networks:
            if network.ssid == target_ssid:
                return network

        return None

    def network_requires_password(self, network):
        """Check if the network requires a password"""
        # If akm list is empty or only contains AKM_TYPE_NONE, no password is required
        return network and (
            network.akm and pywifi.const.AKM_TYPE_NONE not in network.akm
        )

    def has_profile_for_network(self, ssid) -> bool:
        """Check if Windows has a saved profile for this network"""
        existing_profiles = self.iface.network_profiles()
        return any(profile.ssid == ssid for profile in existing_profiles)

    def show_password_dialog(self) -> None | str:
        """Show a Windows 11 style password dialog and return entered password"""
        dialog = PasswordDialog(self.current_ssid)
        if dialog.exec():
            return dialog.password
        return None

    def parse_command(self, command) -> dict[str, str]:
        """Parse user input command"""
        # Handle connect command
        connect_match = re.match(r"^(?:c|connect)=(.+)$", command)
        if connect_match:
            ssid = connect_match.group(1)
            if not self.is_valid_wifi_name(ssid):
                return {"status": "error", "message": "Invalid Wi-Fi name"}

            # Find the network in available networks
            network = self.get_network_info(ssid)
            if not network:
                return {"status": "error", "message": f"Network '{ssid}' not found"}

            self.current_ssid = ssid
            self.requires_password = self.network_requires_password(network)

            # Check if Windows has a saved profile for this network
            has_saved_profile = self.has_profile_for_network(ssid)

            if has_saved_profile:
                # Try to connect using the saved profile
                self.password = None  # No need to provide password
                return {
                    "status": "use_saved_profile",
                    "message": f"Wi-Fi network set to: {ssid}. Found saved profile. Attempting to connect...",
                }
            elif self.requires_password:
                # Show password dialog for password-protected networks
                self.password = self.show_password_dialog()

                if self.password is None:
                    return {
                        "status": "cancelled",
                        "message": f"Connection to {ssid} cancelled by user.",
                    }

                return {
                    "status": "ready_to_connect",
                    "message": f"Wi-Fi network set to: {ssid}. Password provided. Attempting to connect...",
                }
            else:
                # Open network, no password needed
                self.password = None
                return {
                    "status": "ready_to_connect",
                    "message": f"Wi-Fi network set to: {ssid}. This is an open network. Attempting to connect...",
                }

        # Password command no longer needed due to dialog
        password_match = re.match(r"^(?:p|password)=(.+)$", command)
        if password_match:
            return {
                "status": "error",
                "message": "Password entry via command line is disabled. Please use the graphical interface.",
            }

        return {
            "status": "error",
            "message": "Invalid command format. Use c=WIFINAME to connect to a network",
        }

    def connect_with_saved_profile(self) -> dict[str, str]:
        """Try to connect using a saved Windows profile"""
        existing_profiles = self.iface.network_profiles()
        target_profile = None

        for profile in existing_profiles:
            if profile.ssid == self.current_ssid:
                target_profile = profile
                break

        if not target_profile:
            return {
                "status": "error",
                "message": f"No saved profile found for {self.current_ssid}",
            }

        # Connect with the existing profile
        self.iface.connect(target_profile)

        # Wait for connection
        connection_timeout = 10  # seconds
        start_time: float = time.time()

        while time.time() - start_time < connection_timeout:
            status = self.iface.status()
            if status == pywifi.const.IFACE_CONNECTED:
                return {
                    "status": "success",
                    "message": f"Successfully connected to {self.current_ssid} using saved profile",
                }
            time.sleep(0.5)

        return {
            "status": "error",
            "message": f"Failed to connect to {self.current_ssid} using saved profile. You may need to provide a password.",
        }

    def connect_with_new_profile(self) -> dict[str, str]:
        """Connect using a new profile (for networks without saved profiles)"""
        network = self.get_network_info(self.current_ssid)
        if not network:
            return {
                "status": "error",
                "message": f"Network '{self.current_ssid}' not found",
            }

        # Check if password is required but not provided
        if self.network_requires_password(network) and not self.password:
            return {
                "status": "error",
                "message": f"Network '{self.current_ssid}' requires a password.",
            }

        profile = pywifi.Profile()
        profile.ssid = self.current_ssid

        # Configure security based on network type
        if self.network_requires_password(network):
            profile.auth = pywifi.const.AUTH_ALG_OPEN

            # Instead of copying, explicitly set the security type based on what's commonly used
            if (
                pywifi.const.AKM_TYPE_WPA2PSK in network.akm
                or pywifi.const.AKM_TYPE_WPAPSK in network.akm
            ):
                profile.akm = [
                    pywifi.const.AKM_TYPE_WPA2PSK
                ]  # Most common security type
                profile.cipher = (
                    pywifi.const.CIPHER_TYPE_CCMP
                )  # Most common cipher for WPA2
            else:
                # Fallback to copying from network
                profile.akm = network.akm.copy()
                profile.cipher = network.cipher

            profile.key = self.password

        # Add new profile
        profile_added = self.iface.add_network_profile(profile)

        # Connect
        self.iface.connect(profile_added)

        # Wait for connection
        connection_timeout = 10  # seconds
        start_time: float = time.time()

        while time.time() - start_time < connection_timeout:
            status = self.iface.status()
            if status == pywifi.const.IFACE_CONNECTED:
                return {
                    "status": "success",
                    "message": f"Successfully connected to {self.current_ssid}",
                }
            time.sleep(0.5)

        return {
            "status": "error",
            "message": f"Failed to connect to {self.current_ssid}. "
            + (
                "Check your password or network availability."
                if self.requires_password
                else "Check network availability."
            ),
        }

    def connect_to_network(self) -> dict[str, str]:
        """Connect to the specified Wi-Fi network, using saved profile if available"""
        if not self.current_ssid:
            return {"status": "error", "message": "No Wi-Fi network specified"}

        # Check if we should use a saved profile
        if self.has_profile_for_network(self.current_ssid) and not self.password:
            return self.connect_with_saved_profile()
        else:
            return self.connect_with_new_profile()

    def process_input(self, user_input) -> str:
        """Process user input and handle connection flow"""
        result: dict[str, str] = self.parse_command(user_input)

        if result["status"] == "error" or result["status"] == "cancelled":
            return result["message"]

        if result["status"] == "ssid_set":
            return result.get(
                "message",
                f"Wi-Fi network set to: {self.current_ssid}. Password dialog will appear if required.",
            )

        if result["status"] in ["ready_to_connect", "use_saved_profile"]:
            # Attempt to connect
            connection_result: dict[str, str] = self.connect_to_network()
            return result.get("message", "") + "\n" + connection_result["message"]

        return "Unknown command"


def main() -> None:
    import argparse

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Wi-Fi Connection Utility")
    parser.add_argument(
        "-c", "--connect", help="Wi-Fi network name to connect to", type=str
    )
    args: Namespace = parser.parse_args()

    connector = WiFiConnector()
    print("Wi-Fi Connection Utility")
    print("------------------------")

    # If Wi-Fi name is provided as an argument, connect to it directly
    if args.connect:
        result: str = connector.process_input(f"connect={args.connect}")
        print(result)
        return

    # Otherwise, show usage info and enter interactive mode
    print("Commands:")
    print(
        "  c=WIFINAME or connect=WIFINAME - Set Wi-Fi network to connect to (will show password dialog if needed)"
    )
    print("  exit - Exit the program")

    while True:
        try:
            user_input: str = input("\nEnter command: ").strip()
            if user_input.lower() == "exit":
                print("Exiting...")
                break

            result = connector.process_input(user_input)
            print(result)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
