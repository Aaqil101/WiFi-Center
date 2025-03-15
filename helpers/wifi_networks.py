# Built-in Modules
import re
import subprocess

# External Modules
import qtawesome as qta

# PyQt6 Modules
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTableWidget, QWidget


def load_wifi_networks(table: QTableWidget) -> None:
    """
    Loads the list of available Wi-Fi networks into the given QTableWidget.

    :param table: The QTableWidget to load the networks into
    :type table: QTableWidget
    """
    networks: list = get_wifi_networks()
    table.setRowCount(len(networks))

    for row, (ssid, strength, requires_login) in enumerate(networks):
        table.setCellWidget(row, 0, get_network_name_widget(ssid, requires_login))
        table.setCellWidget(row, 1, get_signal_icon(strength))


def get_network_name_widget(ssid: str, requires_login: bool) -> QWidget:
    """
    Generates a QWidget containing a QLabel with the given ssid and a
    QIcon of a lock if the network requires login.

    :param ssid: The name of the network to be displayed
    :type ssid: str
    :param requires_login: Whether the network requires login or not
    :type requires_login: bool
    :return: A QWidget containing the network name and lock icon if needed
    :rtype: QWidget
    """
    container = QWidget()
    layout = QHBoxLayout()

    # Create the SSID label
    ssid_label = QLabel(ssid)
    ssid_label.setStyleSheet(
        """
        color: #ffffff;
        font-size: 14px;
        font-weight: 700;
        font-family: Cambria, Georgia, serif;
        """
    )

    layout.addWidget(ssid_label)

    # Add lock icon if the network requires login
    if requires_login:
        lock_icon = qta.icon("mdi.lock", color="#ffffff")  # Lock icon
        lock_label = QLabel()
        lock_label.setPixmap(lock_icon.pixmap(12, 12))
        layout.addWidget(lock_label)

    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    container.setStyleSheet("background-color: transparent;")
    container.setLayout(layout)

    return container


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
    strength_levels: list[tuple[int, str, str]] = [
        (75, "mdi6.wifi-strength-4", "#00ff00"),
        (50, "mdi6.wifi-strength-3", "#ffaa00"),
        (25, "mdi6.wifi-strength-2", "#ff6600"),
        (1, "mdi6.wifi-strength-1", "#ff0000"),
        (0, "mdi6.wifi-strength-off", "#777777"),
    ]

    for threshold, icon_name, color in strength_levels:
        if strength >= threshold:
            wifi_icon = qta.icon(icon_name, color=color)
            break

    icon_label = QLabel()
    icon_label.setPixmap(wifi_icon.pixmap(16, 16))

    text_label = QLabel(f"{strength}%")
    text_label.setStyleSheet(
        """
        color: #ffffff;
        font-size: 14px;
        font-weight: 700;
        font-family: Cambria, Georgia, serif;
        """
    )

    container = QWidget()
    layout = QHBoxLayout()
    layout.addWidget(icon_label)
    layout.addWidget(text_label)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.setStyleSheet("background-color: transparent;")
    container.setLayout(layout)

    return container


def get_wifi_networks() -> list:
    """
    Retrieves a list of available Wi-Fi networks and their respective signal strengths.

    The list is sorted by signal strength in descending order (strongest first).

    The function returns a list of tuples, where each tuple contains the SSID of the network,
    the signal strength (as a percentage), and a boolean indicating whether a login is required.

    If an error occurs while retrieving the networks, an empty list is returned.

    :return: A list of tuples containing the available Wi-Fi networks and their properties
    :rtype: list[tuple[str, int, bool]]
    """
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

        return networks[:6]

    except Exception as e:
        print(f"Error retrieving Wi-Fi networks: {e}")
        return []
