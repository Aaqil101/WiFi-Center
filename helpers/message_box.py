# Built-in Modules
import sys
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox

if __name__ == "__main__":
    # Add the package root to the Python path
    # NOTE:C:\Users\$USERNAME\Documents\GitHub\WiFi-Center
    sys.path.append(str(Path(__file__).parent.parent))

# Helpers Modules
from helpers import center_on_screen


def msg_box() -> bool:
    """
    Creates a message box with a confirmation question and a warning icon.

    When called, this function creates a message box with a warning icon and a
    confirmation question. The box is centered on the screen and has two buttons
    labeled "Yes" and "No". The function returns a boolean value indicating
    whether the "Yes" button was clicked or not.

    Returns:
        bool: True if the "Yes" button was clicked, False otherwise.
    """
    app = QApplication.instance()
    if app is None:
        # Create QApplication if it doesn't exist
        app = QApplication(sys.argv)

    msg_box = QMessageBox()
    msg_box.setWindowTitle("Confirmation")
    msg_box.setText("Are you sure?")
    msg_box.setFixedSize(180, 125)

    # Get the path to the lock icon and Set the icon
    icon_path: Path = Path(__file__).parent / "assets" / "lock_icon.png"
    msg_box.setWindowIcon(QIcon(str(icon_path)))

    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)

    center_on_screen(msg_box, screen_geometry=app.primaryScreen().geometry())

    result: int = msg_box.exec()

    # ✅ RETURN BOOLEAN VALUE
    return result == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    if msg_box():
        print("User clicked 'Yes'")
    else:
        print("User clicked 'No'")
