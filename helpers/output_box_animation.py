# PyQt6 Modules
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect


def show_output_box_with_animation(self) -> None:
    """
    Displays the output box with a fade-in and slide-in animation.

    Animation steps:
    1. Fade in the output box with an InOutQuad curve.
    2. Slide the output box into view from below, also with an InOutQuad curve.
    3. Slide the command bar and table upwards by 50 pixels.

    The output box is centered horizontally and positioned at the bottom
    with a 10-pixel margin. The animations run simultaneously with a duration
    of 400 milliseconds.
    """
    self.output_box.show()

    # Get the center position
    center_x: int = (self.width() - self.output_box.width()) // 2
    bottom_y: int = (
        self.height() - self.output_box.height() - 10
    )  # 10px margin from bottom

    # Set initial position and size for the output box
    self.output_box.setGeometry(
        center_x,  # Center horizontally
        bottom_y,  # Position at the bottom
        580,  # Fixed width to match other elements
        40,  # Fixed height
    )

    # Fade-in animation for output box
    self.fade_in_animation = QPropertyAnimation(self.output_box, b"windowOpacity")
    self.fade_in_animation.setDuration(400)
    self.fade_in_animation.setStartValue(0)
    self.fade_in_animation.setEndValue(1)
    self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # Slide-in animation for output box
    self.slide_in_animation = QPropertyAnimation(self.output_box, b"geometry")
    self.slide_in_animation.setDuration(400)

    # Calculate start and end positions for output box
    start_rect = QRect(
        center_x,
        self.height(),  # Start below visible area
        580,
        40,
    )
    end_rect = QRect(
        center_x,
        bottom_y,  # End position
        580,
        40,
    )

    self.slide_in_animation.setStartValue(start_rect)
    self.slide_in_animation.setEndValue(end_rect)
    self.slide_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # Slide-up animation for command bar
    self.command_bar_animation = QPropertyAnimation(self.command_bar, b"geometry")
    self.command_bar_animation.setDuration(400)
    command_bar_start_rect: QRect = self.command_bar.geometry()
    command_bar_end_rect = QRect(
        command_bar_start_rect.x(),
        command_bar_start_rect.y() - 50,  # Lift up by 50px
        command_bar_start_rect.width(),
        command_bar_start_rect.height(),
    )
    self.command_bar_animation.setStartValue(command_bar_start_rect)
    self.command_bar_animation.setEndValue(command_bar_end_rect)
    self.command_bar_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # Slide-up animation for table
    self.table_animation = QPropertyAnimation(self.table, b"geometry")
    self.table_animation.setDuration(400)
    table_start_rect: QRect = self.table.geometry()
    table_end_rect = QRect(
        table_start_rect.x(),
        table_start_rect.y() - 50,  # Lift up by 50px
        table_start_rect.width(),
        table_start_rect.height(),
    )
    self.table_animation.setStartValue(table_start_rect)
    self.table_animation.setEndValue(table_end_rect)
    self.table_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # Start animations
    self.fade_in_animation.start()
    self.slide_in_animation.start()
    self.table_animation.start()
    self.command_bar_animation.start()


def hide_output_box_with_animation(self) -> None:
    """
    Hides the output box with a fade-out and slide-out animation.

    Animation steps:
    1. Fade out the output box with an InOutQuad curve.
    2. Slide the output box out of view, also with an InOutQuad curve.
    3. Slide the command bar and table back down to their original positions.
    4. Hide the output box once the animation is complete.
    """
    # Get the center position
    center_x: int = (self.width() - self.output_box.width()) // 2
    bottom_y: int = (
        self.height() - self.output_box.height() - 10
    )  # 10px margin from bottom

    # Fade-out animation for output box
    self.fade_out_animation = QPropertyAnimation(self.output_box, b"windowOpacity")
    self.fade_out_animation.setDuration(400)
    self.fade_out_animation.setStartValue(1)
    self.fade_out_animation.setEndValue(0)
    self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # Slide-out animation for output box
    self.slide_out_animation = QPropertyAnimation(self.output_box, b"geometry")
    self.slide_out_animation.setDuration(400)

    # Calculate start and end positions for output box
    start_rect = QRect(
        center_x,
        bottom_y,  # Current position
        580,
        40,
    )
    end_rect = QRect(
        center_x,
        self.height(),  # End position (out of view)
        580,
        40,
    )

    self.slide_out_animation.setStartValue(start_rect)
    self.slide_out_animation.setEndValue(end_rect)
    self.slide_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # Slide-down animation for command bar
    self.command_bar_animation = QPropertyAnimation(self.command_bar, b"geometry")
    self.command_bar_animation.setDuration(400)
    command_bar_start_rect: QRect = self.command_bar.geometry()
    command_bar_end_rect = QRect(
        command_bar_start_rect.x(),
        command_bar_start_rect.y() + 50,  # Move down by 50px
        command_bar_start_rect.width(),
        command_bar_start_rect.height(),
    )
    self.command_bar_animation.setStartValue(command_bar_start_rect)
    self.command_bar_animation.setEndValue(command_bar_end_rect)
    self.command_bar_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # Slide-down animation for table
    self.table_animation = QPropertyAnimation(self.table, b"geometry")
    self.table_animation.setDuration(400)
    table_start_rect: QRect = self.table.geometry()
    table_end_rect = QRect(
        table_start_rect.x(),
        table_start_rect.y() + 50,  # Move down by 50px
        table_start_rect.width(),
        table_start_rect.height(),
    )
    self.table_animation.setStartValue(table_start_rect)
    self.table_animation.setEndValue(table_end_rect)
    self.table_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # Connect the end of the fade-out animation to hide the output box
    self.fade_out_animation.finished.connect(self.output_box.hide)

    # Start animations
    self.fade_out_animation.start()
    self.slide_out_animation.start()
    self.table_animation.start()
    self.command_bar_animation.start()
