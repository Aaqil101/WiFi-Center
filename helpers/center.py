# PyQt6 Modules
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication


def center_on_screen(
    self, *, screen_geo: QRect = None, x: int = None, y: int = None
) -> None:
    """
    Centers the window on the screen or at specified coordinates.

    This function calculates the center position of the window based on the
    provided screen geometry, or the primary screen's geometry if none is
    provided. If specific x and y coordinates are given, those are used
    instead. The calculated position is cached for future use, and the window
    is moved to that position.

    Args:
        self: The window or widget instance to be centered.
        screen_geo (QRect, optional): The geometry of the screen to center
            the window on. Defaults to the primary screen's geometry.
        x (int, optional): The x-coordinate to position the window. Defaults to
            centering based on screen width.
        y (int, optional): The y-coordinate to position the window. Defaults to
            centering based on screen height.
    """
    if screen_geo is None:
        screen_geometry: QRect = QApplication.primaryScreen().geometry()

    # If x and y are not provided, compute center position
    if x is None:
        x: int = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2

    if y is None:
        y: int = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2

    # Use cached values
    self.move(x, y)
