# Built-in Modules
import re
import subprocess

# PyQt6 Modules
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem


def load_wifi_networks(table: QTableWidget) -> None:
    networks = get_wifi_networks()
    table.setRowCount(len(networks))

    for row, (ssid, strength) in enumerate(networks):
        table.setItem(row, 0, QTableWidgetItem(ssid))  # Set SSID

        # Create QLabel for aligned icon + percentage
        label = QLabel(get_signal_icon(strength))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML rendering

        # Insert QLabel in table
        table.setCellWidget(row, 1, label)


def get_wifi_networks() -> list:
    try:
        process: subprocess.CompletedProcess[str] = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            shell=True,
        )
        output: str = process.stdout
        networks = []

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


def get_signal_icon(strength: int) -> str:
    """
    Returns an HTML formatted string representing the Wi-Fi signal strength icon and percentage.

    Args:
        strength: An integer representing the Wi-Fi signal strength as a percentage.

    Returns:
        A string containing an HTML span element with the corresponding icon and percentage,
        styled with a color indicating the strength: green for full, orange for strong,
        dark orange for medium, red for weak, and grey for no signal.
    """
    if strength >= 75:
        # Full Signal (Green)
        icon = "󰤨"
        color = "#00ff00"
    elif strength >= 50:
        # Strong Signal (Orange)
        icon = "󰤥"
        color = "#ffaa00"
    elif strength >= 25:
        # Medium Signal (Dark Orange)
        icon = "󰤢"
        color = "#ff6600"
    elif strength > 0:
        # Weak Signal (Red)
        icon = "󰤟"
        color = "#ff0000"
    else:
        # No Signal (Grey)
        icon = "󰤭"
        color = "#777777"

    return f"""
    <table style="width: 100%; border-collapse: collapse; text-align: center;">
        <tr>
            <td style="text-align: center; vertical-align: middle; width: 30px;">
                <span style="color: {color}; font-size: 16px;">{icon}</span>
            </td>
            <td style="text-align: center; vertical-align: middle; padding-left: 10px; font-size: 14px;">
                <b>{strength}%</b>
            </td>
        </tr>
    </table>
    """
