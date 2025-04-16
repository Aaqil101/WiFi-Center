# Built-in Modules
import sys
from dataclasses import dataclass
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox

if __name__ == "__main__":
    # Add the package root to the Python path
    sys.path.append(str(Path(__file__).parent.parent))

# Center Modules
from helpers.center import center_on_screen


@dataclass
class Buttons:
    """
    Represents the standard buttons available in a QMessageBox.

    This class encapsulates the common buttons used in message boxes within
    Qt applications. These buttons are used to prompt the user for actions
    such as confirming, canceling, retrying, saving, and more.
    """

    Yes: int = QMessageBox.StandardButton.Yes
    No: int = QMessageBox.StandardButton.No
    Ok: int = QMessageBox.StandardButton.Ok
    Cancel: int = QMessageBox.StandardButton.Cancel
    Close: int = QMessageBox.StandardButton.Close
    Retry: int = QMessageBox.StandardButton.Retry
    Ignore: int = QMessageBox.StandardButton.Ignore
    Save: int = QMessageBox.StandardButton.Save
    Discard: int = QMessageBox.StandardButton.Discard
    Help: int = QMessageBox.StandardButton.Help
    Open: int = QMessageBox.StandardButton.Open
    Apply: int = QMessageBox.StandardButton.Apply
    Reset: int = QMessageBox.StandardButton.Reset
    RestoreDefaults: int = QMessageBox.StandardButton.RestoreDefaults
    SaveAll: int = QMessageBox.StandardButton.SaveAll
    YesToAll: int = QMessageBox.StandardButton.YesToAll
    NoToAll: int = QMessageBox.StandardButton.NoToAll
    Abort: int = QMessageBox.StandardButton.Abort
    Retry: int = QMessageBox.StandardButton.Retry
    Ignore: int = QMessageBox.StandardButton.Ignore
    YesAll: int = QMessageBox.StandardButton.YesAll
    NoAll: int = QMessageBox.StandardButton.NoAll
    Default: int = QMessageBox.StandardButton.Default
    NoButton: int = QMessageBox.StandardButton.NoButton


@dataclass
class Icons:
    """
    Represents the icons available in a QMessageBox.

    This class contains the standard icons that can be displayed in a message box
    to indicate different types of messages. These icons are used to visually
    convey the message's severity or type, such as informational, warning, or critical.
    """

    NoIcon: QMessageBox.Icon = QMessageBox.Icon.NoIcon
    Question: QMessageBox.Icon = QMessageBox.Icon.Question
    Information: QMessageBox.Icon = QMessageBox.Icon.Information
    Warning: QMessageBox.Icon = QMessageBox.Icon.Warning
    Critical: QMessageBox.Icon = QMessageBox.Icon.Critical


class MessageBox:
    def __init__(
        self,
        *,
        title: str = "Message Box",
        text: str = "This is a message box",
        fixed_size: tuple[int, int] = None,
        icon: QMessageBox.Icon = Icons.Warning,
        icon_path: Path = None,
        buttons: QMessageBox.StandardButton = Buttons.Yes | Buttons.No,
        default_button: QMessageBox.StandardButton = Buttons.No,
    ) -> None:
        """
        Initializes a message box with the specified properties.

        Args:
            title: The title of the message box.
            text: The text to display in the message box.
            fixed_size: The fixed size of the message box.
            icon: The icon to display in the message box.
            icon_path: The path to the icon to display in the message box.
            buttons: The standard buttons to display in the message box.
            default_button: The default button of the message box.

        Returns:
            None
        """
        self.app = QApplication.instance()
        if self.app is None:
            # Create QApplication if it doesn't exist
            self.app = QApplication(sys.argv)

        self.title: str = title
        self.text: str = text
        self.fixed_size: tuple[int, int] = fixed_size
        self.icon: QMessageBox.Icon = icon
        self.icon_path: Path = icon_path
        self.buttons: QMessageBox.StandardButton = buttons
        self.default_button: QMessageBox.StandardButton = default_button

    def show(self) -> bool:
        """
        Shows the message box with the specified options.

        This function displays the message box with the specified title, text, and
        buttons. The message box is centered on the screen and uses the provided
        icon. The returned boolean value indicates whether the user clicked the
        "Yes" button.

        Returns:
            bool: True if the user clicked the "Yes" button, False otherwise.
        """
        msg_box = QMessageBox()

        if self.title:
            msg_box.setWindowTitle(self.title)

        if self.text:
            msg_box.setText(self.text)

        if self.fixed_size:
            msg_box.setFixedSize(*self.fixed_size)

        # Get the path to the lock icon and Set the icon
        if self.icon_path:
            icon_path: Path = self.icon_path
        else:
            icon_path: Path = (
                Path(__file__).parent.parent / "assets" / "message_icon.png"
            )

        msg_box.setWindowIcon(QIcon(str(icon_path)))

        if self.icon:
            msg_box.setIcon(self.icon)

        if self.buttons:
            msg_box.setStandardButtons(self.buttons)

        if self.default_button:
            msg_box.setDefaultButton(self.default_button)

        center_on_screen(msg_box, screen_geometry=self.app.primaryScreen().geometry())

        if self.buttons == (Buttons.Yes | Buttons.No):
            result: int = msg_box.exec()

            # ✅ RETURN BOOLEAN VALUE
            return result == QMessageBox.StandardButton.Yes
        else:
            msg_box.exec()


if __name__ == "__main__":
    message_box = MessageBox()
    if message_box.show():
        print("User clicked 'Yes'")
    else:
        print("User clicked 'No'")
