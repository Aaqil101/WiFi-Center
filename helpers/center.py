# Built-in Modules
from typing import Self

# PyQt6 Modules
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication

_cached_position: tuple[int, int] = None


def center_on_screen(self) -> None:
    """
    Centers the widget on the screen.

    If the widget has not been moved yet, it calculates the center of the screen
    and moves the widget there. The calculated position is cached for future calls.

    :return: None
    """
    # Explicitly use the global variable
    global _cached_position

    if _cached_position is None:
        screen_geometry: QRect = QApplication.primaryScreen().geometry()
        x: int = (screen_geometry.width() - self.width()) // 2
        y: int = (screen_geometry.height() - self.height()) // 2

        # Store the computed position
        _cached_position = (x, y)

    # Use cached values
    self.move(*_cached_position)
