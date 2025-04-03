# In-Build Modules
import sys
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Core Modules
from core import CommandProcessor, TerminalAutoComplete, load_wifi_networks

# Helpers Modules
from helpers import (
    apply_window_style,
    center_on_screen,
    get_and_apply_styles,
    hide_output_box_with_animation,
    processing,
    show_output_box_with_animation,
)


class MasterWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Wi-Fi Center")
        self.setFixedSize(600, 400)

        icon_path: Path = Path(__file__).parent / "assets" / "master_icon.png"

        self.setWindowIcon(QIcon(str(icon_path)))

        self.initUI()

        # Initialize the command processor
        self.command_processor = CommandProcessor(self)

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
        self.configure_table()

        # Command Bar
        commands: list[str] = [
            "quit",
            "exit",
            "close",
            "terminate",
            "disconnect",
            "refresh",
            "shutdown",
            "reboot",
            "restart",
            "sleep",
            "hibernate",
            "lock",
            "logout",
            "connect",
            "wifi-manager",
        ]

        self.command_bar = TerminalAutoComplete(commands)
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

        load_wifi_networks(self.table)
        apply_window_style(self)
        center_on_screen(self)

    def configure_table(self) -> None:
        """
        Configures the QTableWidget to have a fixed size and layout, and
        disables editing, selection, and sorting.

        This function is called once, when the window is created, to set up
        the table's appearance and behavior.
        """
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

    def check_input(self) -> None:
        """
        Handles user input from the command bar.

        This method retrieves text input from the command bar, processes it
        by removing leading and trailing whitespace, clears the command bar,
        and passes the cleaned input to the command processor for execution.
        """
        user_input: str = self.command_bar.text().strip()
        self.command_bar.clear()
        self.command_processor.process_input(user_input)


def master() -> None:
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
