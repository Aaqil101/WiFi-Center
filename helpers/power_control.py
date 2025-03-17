# In-Build Modules
import ctypes
import os
import sys
from pathlib import Path

# Helpers Modules
from center import center_on_screen

# PyQt6 Modules
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox


def shutdown() -> None:
    """Shut down the computer after receiving user confirmation."""
    if _msg_box():
        os.system("shutdown /s /t 0")
    else:
        pass


def reboot() -> None:
    """Reboot the computer after receiving user confirmation."""
    if _msg_box():
        os.system("shutdown /r /t 0")
    else:
        pass


def hibernate() -> None:
    """Put the computer into hibernation mode after receiving user confirmation."""
    if _msg_box():
        os.system("shutdown /h")
    else:
        pass


def sleep() -> None:
    """Put the computer into sleep mode after receiving user confirmation."""
    if _msg_box():
        ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
    else:
        pass


def lock() -> None:
    """Lock the computer after receiving user confirmation."""
    if _msg_box():
        os.system("rundll32.exe user32.dll,LockWorkStation")
    else:
        pass


def _msg_box() -> bool:
    """
    Creates a message box to ask the user for confirmation before performing a power-related action.

    Returns:
        bool: True if the user clicked "Yes", False if the user clicked "No"
    """
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Confirmation")
    msg_box.setText("Are you sure you?")

    icon_path: Path = str(Path(__file__).parent.parent / "assets" / "lock_icon.png")

    msg_box.setWindowIcon(QIcon(icon_path))
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.resize(180, 125)
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)
    center_on_screen(msg_box, screen_geometry=app.primaryScreen().geometry())
    result: int = msg_box.exec()
    app.exit()
    return result == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    if _msg_box():
        print("Clicked yes")
    else:
        print("Clicked no")
