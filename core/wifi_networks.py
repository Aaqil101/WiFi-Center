# Built-in Modules
import json
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Psutil Modules
import psutil

# QtAwesome Modules
import qtawesome as qta

# PyQt6 Modules
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTableWidget, QWidget

# PyWiFi Modules
from pywifi import PyWiFi, const, iface

# Helpers Modules
from helpers import Buttons, Icons, MessageBox


class WifiCache:
    """A class to handle WiFi network caching with timeout functionality."""

    def __init__(self, timeout_seconds: int = 10) -> None:
        """Initialize the cache with a specified timeout period."""
        self.data: Optional[List] = None
        self.timestamp: float = 0
        self.timeout: int = timeout_seconds

    def is_valid(self) -> bool:
        """Check if the cache contains valid, non-expired data."""
        return self.data is not None and time.time() - self.timestamp < self.timeout

    def update(self, data: List) -> None:
        """Update the cache with new data and reset the timestamp."""
        self.data = data
        self.timestamp = time.time()

    def clear(self) -> None:
        """Clear the cache data."""
        self.data = None
        self.timestamp = 0


# Constants
WIFI_DATA_FILE: Path = Path(__file__).parent / "wifi_data.json"

# Global WiFi cache instance
_wifi_cache = WifiCache(timeout_seconds=10)

# Global PyWiFi interface (initialized once)
_wifi_interface = None


def get_wifi_interface() -> Optional[iface.Interface]:
    """
    Get the WiFi interface singleton.

    Returns:
        The first available WiFi interface or None if not available
    """
    global _wifi_interface

    if _wifi_interface is not None:
        return _wifi_interface

    try:
        wifi = PyWiFi()
        if wifi.interfaces():
            _wifi_interface = wifi.interfaces()[0]
            return _wifi_interface
    except Exception as e:
        print(f"Error initializing WiFi interface: {e}")

    return None


def load_wifi_networks(table: QTableWidget, *, force_refresh: bool = False) -> None:
    """
    Loads the list of available Wi-Fi networks into the given QTableWidget.

    Args:
        table: The QTableWidget to load the networks into
        force_refresh: If True, forces a refresh of the network data
    """
    networks: List[Tuple[str | int | bool]] = get_wifi_networks(
        force_refresh=force_refresh
    )

    # Optimize table updates by setting row count once
    table.setRowCount(len(networks))

    # Update table widgets
    for row, (ssid, strength, requires_login) in enumerate(networks):
        table.setCellWidget(row, 0, get_network_name_widget(ssid, requires_login))
        table.setCellWidget(row, 1, get_signal_icon(strength))


def is_wifi_scanner_running() -> bool:
    """
    Check if wifi_scanner.py is currently running.

    Returns:
        bool: True if the process is running, False otherwise
    """
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            # Check if the process name is python and the script is wifi_scanner.py
            if (proc.info["name"] in ["python", "python.exe", "python3"]) and any(
                "wifi_scanner.py" in cmd for cmd in proc.info["cmdline"]
            ):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def start_wifi_scanner() -> None:
    """
    Start the wifi_scanner.py script if it's not already running.
    Raises an exception if the script cannot be started.
    """
    try:
        # Determine the full path to the script
        script_path: Path = Path(__file__).parent / "wifi_scanner.py"

        if not script_path.exists():
            raise FileNotFoundError(f"wifi_scanner.py not found at {script_path}")

        # Start the script using the system's default Python interpreter
        subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait a short time to ensure the process starts
        time.sleep(1)
    except Exception as e:
        start_msg_box = MessageBox(
            title="Starting Error",
            text=f"Error starting wifi_scanner.py: {e}",
            fixed_size=(502, 131),
            icon=Icons.Critical,
            buttons=Buttons.Ok,
        )
        start_msg_box.show()
        raise


def get_wifi_networks(force_refresh: bool = False) -> List[Tuple[str, int, bool]]:
    """
    Retrieves a list of available Wi-Fi networks and their respective signal strengths.

    The list is sorted by signal strength in descending order (strongest first).
    Results are cached to improve performance with a timeout of 10 seconds.
    Primarily reads from the JSON file created by the background scanner.

    Args:
        force_refresh: If True, ignores cached data and fetches fresh data

    Returns:
        A list of tuples containing the available Wi-Fi networks and their properties
        Each tuple contains (ssid, signal_strength, requires_login)
    """
    # Check if wifi_scanner.py is running, start it if not
    if not is_wifi_scanner_running():
        try:
            start_wifi_scanner()
        except Exception as e:
            not_started_msg_box = MessageBox(
                title="Starting Error",
                text=f"Could not start wifi_scanner.py: {e}",
                fixed_size=(502, 131),
                icon=Icons.Critical,
                buttons=Buttons.Ok,
            )
            not_started_msg_box.show()
            return []

    # Use cached data if available and not forced to refresh
    if not force_refresh and _wifi_cache.is_valid():
        return _wifi_cache.data

    try:
        # Load from file (primary method)
        with open(WIFI_DATA_FILE, "r") as f:
            wifi_data = json.load(f)

        # Convert loaded data to the expected format and remove duplicates
        seen_ssids = set()
        result: List[Tuple[str, int, bool]] = []
        for item in wifi_data:
            ssid = item["ssid"]
            if ssid not in seen_ssids:
                result.append((ssid, item["strength"], item["requires_login"]))
                seen_ssids.add(ssid)

        # Update cache with the result
        _wifi_cache.update(result)
        return result

    except (FileNotFoundError, json.JSONDecodeError) as e:
        msg_box = MessageBox(
            title="Json File Not Found",
            text=f"Error reading Wi-Fi data from file: {e}. Falling back to scanning.",
            fixed_size=(502, 147),
            icon=Icons.Critical,
            buttons=Buttons.Ok,
        )
        msg_box.show()

        # Fallback to direct scanning only if file doesn't exist or is corrupt
        # This code will only run if the background scanner isn't working
        try:
            Iface: iface.Interface | None = get_wifi_interface()
            if not Iface:
                return []

            # Get saved profiles (connections) once
            saved_profiles: Set[str] = {
                profile.ssid for profile in Iface.network_profiles()
            }

            # Trigger scan
            Iface.scan()

            # Wait just enough time for the scan to complete
            time.sleep(0.8)

            # Get scan results
            scan_results: list = Iface.scan_results()

            # Process scan results more efficiently
            networks_dict: Dict[str, Tuple[str, int, bool]] = {}

            for result in scan_results:
                ssid: str = result.ssid
                if not ssid:  # Skip networks with empty SSIDs
                    continue

                # Convert signal strength (dBm) to percentage (0-100%)
                signal_strength: int = min(max(0, (result.signal + 100) * 2), 100)
                signal_percent = int(signal_strength)

                # Check if authentication is required (simplified check)
                requires_login: bool = (
                    result.akm[0] != const.AKM_TYPE_NONE and ssid not in saved_profiles
                )

                # Keep only the strongest signal for each SSID
                if ssid not in networks_dict or signal_percent > networks_dict[ssid][1]:
                    networks_dict[ssid] = (ssid, signal_percent, requires_login)

            # Convert to list and sort only once
            result: List[Tuple[str, int, bool]] = sorted(
                networks_dict.values(), key=lambda x: x[1], reverse=True
            )[:6]

            # Update cache with the result
            _wifi_cache.update(result)

            return result[:6]  # Return only the top 6

        except Exception as e:
            retrieving_msg_box = MessageBox(
                title="Retrieving Error",
                text=f"Error retrieving Wi-Fi networks: {e}",
                icon=Icons.Critical,
                buttons=Buttons.Ok,
            )
            retrieving_msg_box.show()
            return []


# Styling constants to avoid string repetition
_LABEL_STYLE = """
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    font-family: Cambria, Georgia, serif;
"""

_CONTAINER_STYLE = "background-color: transparent;"


@lru_cache(maxsize=1)
def get_label_style() -> str:
    """Returns the cached style sheet for labels."""
    return _LABEL_STYLE


def get_network_name_widget(ssid: str, requires_login: bool) -> QWidget:
    """
    Generates a QWidget containing a QLabel with the given ssid and a
    QIcon of a lock if the network requires login.

    Args:
        ssid: The name of the network to be displayed
        requires_login: Whether the network requires login or not

    Returns:
        A QWidget containing the network name and lock icon if needed
    """
    container = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    # Create the SSID label
    ssid_label = QLabel(ssid)
    ssid_label.setStyleSheet(_LABEL_STYLE)  # Direct use of constant
    layout.addWidget(ssid_label)

    # Add lock icon if the network requires login
    if requires_login:
        lock_icon: QIcon = get_lock_icon()
        lock_label = QLabel()
        lock_label.setPixmap(lock_icon.pixmap(QSize(12, 12)))
        layout.addWidget(lock_label)

    container.setStyleSheet(_CONTAINER_STYLE)  # Direct use of constant
    container.setLayout(layout)

    return container


@lru_cache(maxsize=1)
def get_lock_icon() -> QIcon:
    """Returns a cached lock icon."""
    return qta.icon("mdi.lock", color="#ffffff")


# Signal strength constants
_SIGNAL_LEVELS: List[Tuple[int | str]] = [
    (75, "mdi6.wifi-strength-4", "#00ff00"),  # Strong signal (green)
    (50, "mdi6.wifi-strength-3", "#ffaa00"),  # Good signal (yellow-orange)
    (25, "mdi6.wifi-strength-2", "#ff6600"),  # Fair signal (orange)
    (1, "mdi6.wifi-strength-1", "#ff0000"),  # Poor signal (red)
    (0, "mdi6.wifi-strength-off", "#777777"),  # No signal (gray)
]


@lru_cache(maxsize=101)  # Cache for all possible strength values (0-100)
def _get_signal_icon_data(strength: int) -> Tuple[str, str]:
    """
    Returns the icon name and color for a given signal strength.

    Args:
        strength: The signal strength as an integer from 0 to 100

    Returns:
        tuple: A tuple containing the icon name and color
    """
    for threshold, icon_name, color in _SIGNAL_LEVELS:
        if strength >= threshold:
            return (icon_name, color)

    # Default fallback
    return ("mdi6.wifi-strength-off", "#777777")


@lru_cache(maxsize=101)  # Cache icons for all possible strength values
def get_cached_wifi_icon(strength: int) -> QIcon:
    """Returns a cached WiFi icon for a given strength."""
    icon_name, color = _get_signal_icon_data(strength)
    return qta.icon(icon_name, color=color)


def get_signal_icon(strength: int) -> QWidget:
    """
    Returns a QWidget containing a signal strength icon and its corresponding percentage value.

    Args:
        strength: Signal strength (0-100)

    Returns:
        A QWidget containing the icon and percentage text
    """
    # Use pre-cached icon
    wifi_icon: QIcon = get_cached_wifi_icon(strength)

    container = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Create and add icon label
    icon_label = QLabel()
    icon_label.setPixmap(wifi_icon.pixmap(QSize(16, 16)))
    layout.addWidget(icon_label)

    # Create and add text label
    text_label = QLabel(f"{strength}%")
    text_label.setStyleSheet(_LABEL_STYLE)  # Direct use of constant
    layout.addWidget(text_label)

    container.setStyleSheet(_CONTAINER_STYLE)  # Direct use of constant
    container.setLayout(layout)

    return container


def clear_caches() -> None:
    """
    Clears all caches used in this module.
    """
    # Clear WiFi cache
    _wifi_cache.clear()

    # Reset WiFi interface
    global _wifi_interface
    _wifi_interface = None

    # Clear lru_cache caches
    get_label_style.cache_clear()
    get_lock_icon.cache_clear()
    _get_signal_icon_data.cache_clear()
    get_cached_wifi_icon.cache_clear()
