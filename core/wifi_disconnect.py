# Built-in Modules
from pathlib import Path

# Third-Party Modules
import pywifi

# PyQt6 Modules
from PyQt6.QtCore import QTimer
from pywifi import const

# Helpers Modules
from helpers import (
    get_and_apply_styles,
    hide_output_box_with_animation,
    processing,
    show_output_box_with_animation,
)


def disconnect(self) -> None:
    """Disconnects from the current Wi-Fi network using pywifi."""
    processing(self, begin=True)
    success = False
    message = "❌ Failed to disconnect from Wi-Fi."
    style_file = "output_box_failure.qss"

    try:
        wifi = pywifi.PyWiFi()
        interfaces = wifi.interfaces()
        if not interfaces:
            message = "❌ No Wi-Fi interfaces found."
        else:
            iface = interfaces[0]  # Use the first available interface
            if iface.status() in [const.IFACE_CONNECTED, const.IFACE_CONNECTING]:
                iface.disconnect()
                # Check status again after attempting disconnect
                # Give it a moment to update status
                import time

                time.sleep(1)
                if iface.status() == const.IFACE_DISCONNECTED:
                    success = True
                    message = "✅ Successfully disconnected from Wi-Fi."
                    style_file = "output_box_success.qss"
                else:
                    # Sometimes disconnect might fail silently or status update is slow
                    message = "❌ Disconnect command sent, but status didn't change."
            elif iface.status() == const.IFACE_DISCONNECTED:
                success = True  # Already disconnected
                message = "ℹ️ Already disconnected from Wi-Fi."
                style_file = "output_box_success.qss"  # Use success style for info
            else:
                message = f"❌ Unknown interface status: {iface.status()}"

    except IndexError:
        message = "❌ No Wi-Fi interfaces found."
    except Exception as e:
        # Catching a broad exception might be necessary as pywifi errors aren't well-documented
        message = f"❌ An error occurred: {e}"
        print(f"⚠ Error during Wi-Fi disconnect: {e}")

    # Apply styles and set text
    get_and_apply_styles(
        script_file=Path(__file__).parent,  # Go up one level to project root
        set_content_funcs={style_file: self.output_box.setStyleSheet},
    )
    self.output_box.setPlainText(message)

    # Show the output box with animation
    show_output_box_with_animation(self)

    # Hide the output box after 0.5 seconds and then enable the command bar
    QTimer.singleShot(500, lambda: hide_output_box_with_animation(self))

    # Enable the command bar after the hide animation is complete (1200ms total)
    QTimer.singleShot(1200, lambda: processing(self, end=True))
