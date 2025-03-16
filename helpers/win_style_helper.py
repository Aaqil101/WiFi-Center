# Built-in Modules
import sys
from functools import lru_cache
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtCore import Qt

# Helpers Modules
from helpers import Blur, get_and_apply_styles


@lru_cache(maxsize=1)
def is_windows_11() -> bool:
    """
    Check if the system is running Windows 11.

    Returns:
        bool: True if Windows 11 (build >= 22000), False otherwise
    """
    windows_build: int = sys.getwindowsversion().build
    return windows_build >= 22000


def apply_window_style(self) -> None:
    """
    Applies the appropriate window style based on the Windows version.

    This function checks the Windows build version to determine if the system
    is running Windows 11 or an earlier version. Depending on the version, it
    applies the corresponding stylesheets and settings to the window and its
    components.

    On Windows 11:
        - Sets the window to have a translucent background.
        - Applies styles from 'win11.qss' and 'wifi_table_win11.qss'.
        - Enables blur effects on the window.

    On Windows 10 or earlier:
        - Applies styles from 'win10.qss' and 'wifi_table_win10.qss'.
    """
    if is_windows_11():
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        get_and_apply_styles(
            script_file=Path(__file__).parent,
            set_content_funcs={
                "win11.qss": self.setStyleSheet,
                "wifi_table_win11.qss": self.table.setStyleSheet,
            },
        )
        Blur(self.winId(), DarkMode=True)
    else:
        get_and_apply_styles(
            script_file=Path(__file__).parent,
            set_content_funcs={
                "win10.qss": self.setStyleSheet,
                "wifi_table_win10.qss": self.table.setStyleSheet,
            },
        )
