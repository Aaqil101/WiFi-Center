import re
import sys
import time

import pywifi
from pywifi import const


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
        return network and (network.akm and const.AKM_TYPE_NONE not in network.akm)

    def has_profile_for_network(self, ssid):
        """Check if Windows has a saved profile for this network"""
        existing_profiles = self.iface.network_profiles()
        return any(profile.ssid == ssid for profile in existing_profiles)

    def parse_command(self, command):
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
                # Password required but not saved
                return {
                    "status": "ssid_set",
                    "ssid": ssid,
                    "message": f"Wi-Fi network set to: {ssid}. This network requires a password. Use p=PASSWORD to provide it.",
                }
            else:
                # Open network, no password needed
                self.password = None
                return {
                    "status": "ready_to_connect",
                    "message": f"Wi-Fi network set to: {ssid}. This is an open network. Attempting to connect...",
                }

        # Handle password command
        password_match = re.match(r"^(?:p|password)=(.+)$", command)
        if password_match:
            if not self.current_ssid:
                return {
                    "status": "error",
                    "message": "Please specify a Wi-Fi network first using c=WIFINAME",
                }
            self.password = password_match.group(1)
            return {
                "status": "ready_to_connect",
                "password": self.password,
                "message": "Password set. Attempting to connect...",
            }

        return {
            "status": "error",
            "message": "Invalid command format. Use c=WIFINAME or p=PASSWORD",
        }

    def connect_with_saved_profile(self):
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
        start_time = time.time()

        while time.time() - start_time < connection_timeout:
            status = self.iface.status()
            if status == const.IFACE_CONNECTED:
                return {
                    "status": "success",
                    "message": f"Successfully connected to {self.current_ssid} using saved profile",
                }
            time.sleep(0.5)

        return {
            "status": "error",
            "message": f"Failed to connect to {self.current_ssid} using saved profile. You may need to provide a password.",
        }

    def connect_with_new_profile(self):
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
                "message": f"Network '{self.current_ssid}' requires a password. Please use p=PASSWORD",
            }

        profile = pywifi.Profile()
        profile.ssid = self.current_ssid

        # Configure security based on network type
        if self.network_requires_password(network):
            profile.auth = const.AUTH_ALG_OPEN
            # Copy the security type from the actual network
            profile.akm = network.akm.copy()
            profile.cipher = network.cipher
            profile.key = self.password

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
            "message": f"Failed to connect to {self.current_ssid}. "
            + (
                "Check your password or network availability."
                if self.requires_password
                else "Check network availability."
            ),
        }

    def connect_to_network(self):
        """Connect to the specified Wi-Fi network, using saved profile if available"""
        if not self.current_ssid:
            return {"status": "error", "message": "No Wi-Fi network specified"}

        # Check if we should use a saved profile
        if self.has_profile_for_network(self.current_ssid) and not self.password:
            return self.connect_with_saved_profile()
        else:
            return self.connect_with_new_profile()

    def process_input(self, user_input):
        """Process user input and handle connection flow"""
        result = self.parse_command(user_input)

        if result["status"] == "error":
            return result["message"]

        if result["status"] == "ssid_set":
            return result.get(
                "message",
                f"Wi-Fi network set to: {self.current_ssid}. If password required, use p=PASSWORD",
            )

        if result["status"] in ["ready_to_connect", "use_saved_profile"]:
            # Attempt to connect
            connection_result = self.connect_to_network()
            return result.get("message", "") + "\n" + connection_result["message"]

        return "Unknown command"


def main() -> None:
    connector = WiFiConnector()
    print("Wi-Fi Connection Utility")
    print("------------------------")
    print("Commands:")
    print("  c=WIFINAME or connect=WIFINAME - Set Wi-Fi network to connect to")
    print("  p=PASSWORD or password=PASSWORD - Provide password if required")
    print("  exit - Exit the program")

    while True:
        try:
            user_input = input("\nEnter command: ").strip()
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
