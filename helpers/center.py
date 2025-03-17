# PyQt6 Modules
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication

_cached_position: tuple[int, int] = None


def center_on_screen(self, *, screen_geometry: QRect = None) -> None:
    """
    Centers the widget on the screen using the screen geometry.

    This function calculates and sets the widget's position to the center of the screen
    based on the provided screen geometry. If no screen geometry is provided, it defaults
    to the primary screen's geometry. The calculated position is cached for subsequent calls.

    Args:
        self: The widget to be centered.
        screen_geometry (QRect, optional): The geometry of the screen to use for centering.
            Defaults to None, which uses the primary screen's geometry.

    Returns:
        None
    """
    # Explicitly use the global variable
    global _cached_position

    if _cached_position is None:
        if screen_geometry is None:
            screen_geometry: QRect = QApplication.primaryScreen().geometry()
        x: int = (screen_geometry.width() - self.width()) // 2
        y: int = (screen_geometry.height() - self.height()) // 2

        # Store the computed position
        _cached_position = (x, y)

    # Use cached values
    self.move(*_cached_position)
