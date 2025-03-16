# Built-in Modules
import re
import subprocess
import time
from functools import lru_cache
from typing import Any

# External Modules
import qtawesome as qta

# PyQt6 Modules
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTableWidget, QWidget


def load_wifi_networks(table: QTableWidget, *, force_refresh: bool = False) -> None:
    """
    Loads the list of available Wi-Fi networks into the given QTableWidget.

    Args:
        table: The QTableWidget to load the networks into
        force_refresh: If True, forces a refresh of the network data
    """
    networks: list = get_wifi_networks(force_refresh=force_refresh)
    table.setRowCount(len(networks))

    for row, (ssid, strength, requires_login) in enumerate(networks):
        table.setCellWidget(row, 0, get_network_name_widget(ssid, requires_login))
        table.setCellWidget(row, 1, get_signal_icon(strength))


# Cache for WiFi networks with manual expiration tracking
_wifi_cache: dict[str, Any] = {"data": None, "timestamp": 0}
_CACHE_TIMEOUT = 10  # seconds


def get_wifi_networks(force_refresh: bool = False) -> list:
    """
    Retrieves a list of available Wi-Fi networks and their respective signal strengths.

    The list is sorted by signal strength in descending order (strongest first).
    Results are cached to improve performance with a timeout of 10 seconds.

    Args:
        force_refresh: If True, ignores cached data and fetches fresh data

    Returns:
        A list of tuples containing the available Wi-Fi networks and their properties
        Each tuple contains (ssid, signal_strength, requires_login)
    """
    current_time: float = time.time()

    # Return cached data if it's fresh and no force refresh
    if not force_refresh and _wifi_cache["data"] is not None:
        if current_time - _wifi_cache["timestamp"] < _CACHE_TIMEOUT:
            return _wifi_cache["data"]

    try:
        # Get saved Wi-Fi profiles
        saved_profiles_process: subprocess.CompletedProcess[str] = subprocess.run(
            ["netsh", "wlan", "show", "profiles"],
            capture_output=True,
            text=True,
            shell=True,
        )
        saved_profiles_output: str = saved_profiles_process.stdout
        saved_profiles = set(
            re.findall(r"All User Profile\s*:\s*(.+)", saved_profiles_output)
        )

        # Get available Wi-Fi networks
        process: subprocess.CompletedProcess[str] = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            shell=True,
        )
        output: str = process.stdout

        ssid_pattern: re.Pattern[str] = re.compile(r"SSID \d+ : (.+)")
        signal_pattern: re.Pattern[str] = re.compile(r"Signal\s*:\s*(\d+)%")
        security_pattern: re.Pattern[str] = re.compile(r"Authentication\s*:\s*(?!Open)")

        networks: list = []
        ssid = None
        requires_login = False  # True if network is secured and not saved

        for line in output.splitlines():
            ssid_match: re.Match[str] | None = ssid_pattern.search(line)
            if ssid_match:
                ssid: str | re.Any = ssid_match.group(1)
                requires_login = False  # Reset for each SSID
                continue

            if security_pattern.search(line):  # If the network is secured
                requires_login = True  # Assume login is needed

            signal_match: re.Match[str] | None = signal_pattern.search(line)
            if ssid and signal_match:
                signal = int(signal_match.group(1))

                # Check if SSID is in saved profiles
                if ssid in saved_profiles:
                    requires_login = False  # No lock icon needed

                networks.append((ssid, signal, requires_login))
                ssid = None  # Reset for next network

        # Sort networks by signal strength in descending order
        networks.sort(key=lambda x: x[1], reverse=True)

        result: list = networks[:6]

        # Cache the result with timestamp
        _wifi_cache["data"] = result
        _wifi_cache["timestamp"] = current_time

        return result

    except Exception as e:
        print(f"Error retrieving Wi-Fi networks: {e}")
        return []


# Cache widget style sheets to avoid repeated string creation
@lru_cache(maxsize=1)
def get_label_style() -> str:
    """
    Returns the style sheet for labels.

    Returns:
        str: The style sheet
    """
    return """
        color: #ffffff;
        font-size: 14px;
        font-weight: 700;
        font-family: Cambria, Georgia, serif;
    """


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

    # Create the SSID label
    ssid_label = QLabel(ssid)
    ssid_label.setStyleSheet(get_label_style())

    layout.addWidget(ssid_label)

    # Add lock icon if the network requires login
    if requires_login:
        lock_icon = get_lock_icon()
        lock_label = QLabel()
        lock_label.setPixmap(lock_icon.pixmap(12, 12))
        layout.addWidget(lock_label)

    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    container.setStyleSheet("background-color: transparent;")
    container.setLayout(layout)

    return container


@lru_cache(maxsize=1)
def get_lock_icon():
    """
    Returns a cached lock icon.

    Returns:
        QIcon: The lock icon
    """
    return qta.icon("mdi.lock", color="#ffffff")


@lru_cache(maxsize=5)  # Only 5 different strength levels
def _get_signal_icon_data(strength: int) -> tuple:
    """
    Returns the icon name and color for a given signal strength.

    Args:
        strength: The signal strength as an integer from 0 to 100

    Returns:
        tuple: A tuple containing the icon name and color
    """
    strength_levels: list[tuple[int, str, str]] = [
        (75, "mdi6.wifi-strength-4", "#00ff00"),
        (50, "mdi6.wifi-strength-3", "#ffaa00"),
        (25, "mdi6.wifi-strength-2", "#ff6600"),
        (1, "mdi6.wifi-strength-1", "#ff0000"),
        (0, "mdi6.wifi-strength-off", "#777777"),
    ]

    for threshold, icon_name, color in strength_levels:
        if strength >= threshold:
            return (icon_name, color)

    # Default fallback
    return ("mdi6.wifi-strength-off", "#777777")


def get_signal_icon(strength: int) -> QWidget:
    """
    Returns a QWidget containing a signal strength icon and its corresponding percentage value as a string.

    The strength parameter is the signal strength as an integer from 0 to 100.

    The returned QWidget is a container with a horizontal layout containing a QLabel for the icon and another QLabel for the percentage string.

    The icon is chosen based on the signal strength, with the following thresholds:

        - 75% and above: mdi6.wifi-strength-4 (four bars, green)
        - 50% to 74%: mdi6.wifi-strength-3 (three bars, yellow-orange)
        - 25% to 49%: mdi6.wifi-strength-2 (two bars, orange)
        - 1% to 24%: mdi6.wifi-strength-1 (one bar, red)
        - 0%: mdi6.wifi-strength-off (no bars, gray)

    The color of the icon is also chosen based on the threshold, with the same colors as above.

    The percentage string is displayed in white, 14px, bold, Cambria font.

    The container is transparent and has a centered horizontal layout with no margins.
    """
    # Get cached icon data
    icon_name, color = _get_signal_icon_data(strength)
    wifi_icon = qta.icon(icon_name, color=color)

    icon_label = QLabel()
    icon_label.setPixmap(wifi_icon.pixmap(16, 16))

    text_label = QLabel(f"{strength}%")
    text_label.setStyleSheet(get_label_style())

    container = QWidget()
    layout = QHBoxLayout()
    layout.addWidget(icon_label)
    layout.addWidget(text_label)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.setStyleSheet("background-color: transparent;")
    container.setLayout(layout)

    return container


# Method to manually clear all caches
def clear_caches() -> None:
    """
    Clears all caches used in this module.

    This includes:
    - The WiFi networks cache
    - The label style cache
    - The lock icon cache
    - The signal icon data cache
    """
    # Clear WiFi networks cache
    _wifi_cache["data"] = None
    _wifi_cache["timestamp"] = 0

    # Clear lru_cache caches
    get_label_style.cache_clear()
    get_lock_icon.cache_clear()
    _get_signal_icon_data.cache_clear()
