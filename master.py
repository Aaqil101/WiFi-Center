# In-Build Modules
import subprocess
import sys
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Helpers Modules
from helpers import get_and_apply_styles, load_wifi_networks


class MasterWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Wi-Fi Center")
        self.setFixedSize(600, 400)

        icon_path: Path = Path(__file__).parent / "assets" / "master_icon.png"

        self.setWindowIcon(QIcon(str(icon_path)))

        self.initUI()
        load_wifi_networks(self.table)

    def initUI(self) -> None:
        # Hidden Text Box
        self.output_box = QTextEdit()
        self.output_box.setFixedHeight(40)
        self.output_box.setFixedWidth(580)
        self.output_box.setReadOnly(True)

        self.output_box.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.output_box.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.output_box.hide()

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setFixedHeight(325)
        self.table.setHorizontalHeaderLabels(["Network Name", "Signal Strength"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only

        # 🚀 Disable selection completely
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 🚀 Fix row positions
        self.table.verticalHeader().setSectionsMovable(False)  # Prevent dragging
        self.table.setSortingEnabled(False)  # Prevent sorting from changing row order
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(40)  # Fixed row height

        # 🚀 Fix column positions and sizes
        self.table.horizontalHeader().setSectionsMovable(False)  # Lock column order
        self.table.setColumnWidth(0, 400)  # Fixed width for Network Name
        self.table.setColumnWidth(1, 155)  # Fixed width for Signal Strength
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )

        # ®️ Remove row numbers and scrollbars
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Command Bar
        self.command_bar = QLineEdit()
        self.command_bar.setFixedWidth(580)
        self.command_bar.setFixedHeight(40)
        self.command_bar.setPlaceholderText("Type here...")

        self.command_bar.returnPressed.connect(self.check_input)

        # Layouts - Adjust to center align all elements
        master_layout = QVBoxLayout()
        master_layout.setContentsMargins(10, 10, 10, 10)  # Set consistent margins
        master_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Center align output box
        output_layout = QHBoxLayout()
        output_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        output_layout.addWidget(self.output_box)

        # Center align command bar
        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.command_bar)

        table = QVBoxLayout()
        table.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table.addWidget(self.table)

        get_and_apply_styles(
            script_file=__file__,
            set_content_funcs={
                "command_bar.qss": self.command_bar.setStyleSheet,
                "output_box.qss": self.output_box.setStyleSheet,
            },
        )

        master_layout.addLayout(table)
        master_layout.addLayout(output_layout)
        master_layout.addStretch()
        master_layout.addLayout(input_layout)

        self.setLayout(master_layout)

        self.apply_window_style()
        self.center_on_screen()

    def testing(self) -> None:
        import random

        # Disable the command bar at the beginning of the function
        self.command_bar.setDisabled(True)

        number: int = random.randint(0, 1)

        if number == 1:
            get_and_apply_styles(
                script_file=__file__,
                set_content_funcs={
                    "output_box_success.qss": self.output_box.setStyleSheet
                },
            )
            self.output_box.setPlainText("✅ Success")

        if number == 0:
            get_and_apply_styles(
                script_file=__file__,
                set_content_funcs={
                    "output_box_failure.qss": self.output_box.setStyleSheet
                },
            )
            self.output_box.setPlainText("❌ Failure")

        # Show the output box with animation
        self.show_output_box_with_animation()

        # Create a function to handle re-enabling the command bar
        def enable_command_bar() -> None:
            self.command_bar.setDisabled(False)
            self.command_bar.setFocus()

        # Hide the output box after 2 seconds and then enable the command bar
        QTimer.singleShot(1000, self.hide_output_box_with_animation)
        # Enable the command bar after the hide animation is complete (1400ms total)
        QTimer.singleShot(1400, enable_command_bar)

    def apply_window_style(self) -> None:
        """
        Applies the appropriate window style based on the Windows version.
        """
        from helpers import Blur

        windows_build: int = sys.getwindowsversion().build
        is_windows_11: bool = windows_build >= 22000

        if is_windows_11:
            get_and_apply_styles(
                script_file=__file__,
                set_content_funcs={
                    "wifi_table_win11.qss": self.table.setStyleSheet,
                    "win11.qss": self.setStyleSheet,
                },
            )

            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            Blur(self.winId())
        else:
            get_and_apply_styles(
                script_file=__file__,
                set_content_funcs={
                    "wifi_table_win10.qss": self.table.setStyleSheet,
                    "win10.qss": self.setStyleSheet,
                },
            )

    def center_on_screen(self) -> None:
        """
        Centers the window on the screen.
        """
        screen_geometry: QRect = QApplication.primaryScreen().geometry()
        x: int = (screen_geometry.width() - self.width()) // 2
        y: int = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def check_input(self) -> None:
        user_input: str = self.command_bar.text()
        self.command_bar.clear()

        if "d" in user_input.lower():
            self.testing()

        if "q" in user_input.lower():
            QApplication.quit()

    def disconnect_wifi(self) -> None:
        # Disable the command bar at the beginning of the function
        self.command_bar.setDisabled(True)

        try:
            process = subprocess.run(
                ["netsh", "wlan", "disconnect"],
                shell=True,
                capture_output=True,
                text=True,
            )

            if process.returncode == 0:
                get_and_apply_styles(
                    script_file=__file__,
                    set_content_funcs={
                        "output_box_success.qss": self.output_box.setStyleSheet
                    },
                )
                self.output_box.setPlainText("✅ Successfully disconnected from Wi-Fi.")
            else:
                get_and_apply_styles(
                    script_file=__file__,
                    set_content_funcs={
                        "output_box_failure.qss": self.output_box.setStyleSheet
                    },
                )
                self.output_box.setPlainText(
                    "❌ Failed to disconnect from Wi-Fi. Try running as administrator."
                )
        except subprocess.CalledProcessError as e:
            print(f"⚠ Error: {e}")

        # Show the output box with animation
        self.show_output_box_with_animation()

        def enable_command_bar() -> None:
            self.command_bar.setDisabled(False)
            self.command_bar.setFocus()

        # Hide the output box after 2 seconds and then enable the command bar
        QTimer.singleShot(1000, self.hide_output_box_with_animation)

        # Enable the command bar after the hide animation is complete (1400ms total)
        QTimer.singleShot(1400, enable_command_bar)

    def show_output_box_with_animation(self) -> None:
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

        # # Slide-up animation for table
        # self.table_animation = QPropertyAnimation(self.table, b"geometry")
        # self.table_animation.setDuration(400)
        # table_start_rect: QRect = self.table.geometry()
        # table_end_rect = QRect(
        #     table_start_rect.x(),
        #     table_start_rect.y() - 50,  # Lift up by 50px
        #     table_start_rect.width(),
        #     table_start_rect.height(),
        # )
        # self.table_animation.setStartValue(table_start_rect)
        # self.table_animation.setEndValue(table_end_rect)
        # self.table_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Start animations
        self.fade_in_animation.start()
        self.slide_in_animation.start()
        # self.table_animation.start()
        self.command_bar_animation.start()

    def hide_output_box_with_animation(self) -> None:
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

        # # Slide-down animation for table
        # self.table_animation = QPropertyAnimation(self.table, b"geometry")
        # self.table_animation.setDuration(400)
        # table_start_rect: QRect = self.table.geometry()
        # table_end_rect = QRect(
        #     table_start_rect.x(),
        #     table_start_rect.y() + 50,  # Move down by 50px
        #     table_start_rect.width(),
        #     table_start_rect.height(),
        # )
        # self.table_animation.setStartValue(table_start_rect)
        # self.table_animation.setEndValue(table_end_rect)
        # self.table_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Connect the end of the fade-out animation to hide the output box
        self.fade_out_animation.finished.connect(self.output_box.hide)

        # Start animations
        self.fade_out_animation.start()
        self.slide_out_animation.start()
        # self.table_animation.start()
        self.command_bar_animation.start()


def master():
    from PyQt6.QtCore import QElapsedTimer

    timer = QElapsedTimer()
    timer.start()  # Start timing

    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    window.command_bar.setFocus()

    elapsed_time: float = timer.elapsed() / 1000  # Convert to seconds
    print(f"Launch time: {elapsed_time:.4f} seconds")

    sys.exit(app.exec())


if __name__ == "__main__":
    master()
