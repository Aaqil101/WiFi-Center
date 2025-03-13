# Built-in Modules
import re
import subprocess

# External Modules
import qtawesome as qta

# PyQt6 Modules
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QWidget


def load_wifi_networks(table: QTableWidget) -> None:
    """
    Populates a QTableWidget with the 6 strongest Wi-Fi networks in range, each with its signal strength as a percentage.

    :param table: The QTableWidget to populate
    :type table: QTableWidget
    """
    networks: list = get_wifi_networks()
    table.setRowCount(len(networks))

    for row, (ssid, strength) in enumerate(networks):
        table.setItem(row, 0, QTableWidgetItem(ssid))  # Set SSID

        # Create QWidget for aligned icon + percentage
        widget: QWidget = get_signal_icon(strength)

        # Insert QWidget in table
        table.setCellWidget(row, 1, widget)


def get_wifi_networks() -> list:
    """
    Gets a list of the 6 strongest Wi-Fi networks in range. Returns a list of tuples, each containing the SSID and signal strength as a percentage.

    :return: A list of tuples containing the SSID and signal strength as a percentage.
    :rtype: list[tuple[str, int]]
    """
    try:
        process: subprocess.CompletedProcess[str] = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            shell=True,
        )
        output: str = process.stdout
        networks: list = []

        ssid, signal = None, None
        for line in output.split("\n"):
            ssid_match: re.Match[str] | None = re.search(r"SSID \d+ : (.+)", line)
            signal_match: re.Match[str] | None = re.search(r"Signal\s*:\s*(\d+)%", line)

            if ssid_match:
                ssid: str | re.Any = ssid_match.group(1)
            if signal_match:
                signal = int(signal_match.group(1))

            if ssid and signal is not None:
                networks.append((ssid, signal))
                ssid, signal = None, None  # Reset for next network

        return networks[:6]

    except Exception as e:
        print(f"Error retrieving Wi-Fi networks: {e}")
        return []


def get_signal_icon(strength: int) -> QWidget:
    """
    Returns a QWidget containing an icon and a percentage label indicating the strength of the given Wi-Fi network.

    The icon is determined by the strength of the network, and is one of the following:
        - Full Signal (>= 75%): mdi6.wifi-strength-4
        - Strong Signal (>= 50%): mdi6.wifi-strength-3
        - Medium Signal (>= 25%): mdi6.wifi-strength-2
        - Weak Signal (>= 0%): mdi6.wifi-strength-1
        - No Signal (< 0%): mdi6.wifi-strength-off

    The percentage label is aligned with the icon and is displayed in white, with a bold font and a family of Cambria, Cochin, Georgia, Times, or Times New Roman.

    :param strength: The strength of the Wi-Fi network as a percentage (0-100)
    :return: A QWidget containing the icon and percentage label
    """
    if strength >= 75:
        # Full Signal
        icon = qta.icon("mdi6.wifi-strength-4", color="#00ff00")
    elif strength >= 50:
        # Strong Signal
        icon = qta.icon("mdi6.wifi-strength-3", color="#ffaa00")
    elif strength >= 25:
        # Medium Signal
        icon = qta.icon("mdi6.wifi-strength-2", color="#ff6600")
    elif strength > 0:
        # Weak Signal
        icon = qta.icon("mdi6.wifi-strength-1", color="#ff0000")
    else:
        # No Signal
        icon = qta.icon("mdi6.wifi-strength-off", color="#777777")

    icon_label = QLabel()
    pixmap = icon.pixmap(16, 16)  # Adjust size if needed
    icon_label.setPixmap(pixmap)

    text_label = QLabel(f"{strength}%")
    text_label.setStyleSheet(
        """
        color: rgb(255, 255, 255);
        font-size: 14px;
        font-weight: 700;
        font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;
        """
    )

    container = QWidget()
    layout = QHBoxLayout()
    layout.addWidget(icon_label)
    layout.addWidget(text_label)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.setStyleSheet(
        """
        background-color: transparent;
        """
    )
    container.setLayout(layout)

    return container
