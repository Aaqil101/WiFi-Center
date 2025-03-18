# Build-in Modules
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Add the package root to the Python path
    sys.path.append(str(Path(__file__).parent.parent))

# Message Box Module
from helpers.message_box import Buttons, Icons, MessageBox


def open_wifi_manager(*, terminal: str = None) -> None:
    """
    Opens the Wi-Fi manager using the specified terminal.

    This function launches the Windows Wi-Fi manager using the given terminal command
    (cmd, powershell, or pwsh). The Wi-Fi manager interface allows users to view and
    connect to available Wi-Fi networks.

    Args:
        terminal: The terminal to use for opening the Wi-Fi manager. Can be 'cmd', 'powershell', or 'pwsh'. If None, an error message is printed in the message box.
    """

    path: Path = Path(__file__).parent.parent / "assets" / "terminal_icon.png"
    icon = Icons.Critical
    button: int = Buttons.Ok

    terminal_is_none = MessageBox(
        title="Terminal Is None",
        text="Error: No terminal specified. Use 'cmd', 'powershell', or 'pwsh'.",
        fixed_size=(403, 125),
        icon=icon,
        buttons=button,
        icon_path=path,
    )

    unknown_terminal = MessageBox(
        title="Unknown Terminal",
        text=f"Error: Unknown terminal '{terminal}'. Use 'cmd', 'powershell', or 'pwsh'.",
        fixed_size=(426, 125),
        icon=icon,
        buttons=button,
        icon_path=path,
    )

    if terminal is None:
        if terminal_is_none.show():
            print("Help")
        return

    try:
        if terminal == "cmd":
            subprocess.run(
                ["cmd", "/c", "start", "ms-availablenetworks:///"], check=True
            )

        elif terminal == "powershell":
            subprocess.run(
                ["powershell", "-Command", "Start-Process", "ms-availablenetworks:///"],
                check=True,
            )

        elif terminal == "pwsh":
            subprocess.run(
                ["pwsh", "-Command", "Start-Process", "ms-availablenetworks:///"],
                check=True,
            )

        else:
            unknown_terminal.show()

    except subprocess.CalledProcessError as e:
        called_process_error = MessageBox(
            title="Called Process Error",
            text=f"An error occurred while trying to open the Wi-Fi manager: {e}",
            fixed_size=(502, 147),
            icon=icon,
            buttons=button,
            icon_path=path,
        )
        called_process_error.show()


if __name__ == "__main__":
    open_wifi_manager(terminal="cmd")
