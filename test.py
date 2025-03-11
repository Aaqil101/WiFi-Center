# Built-in Modules
import sys

# PyQt6 Modules
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QTableWidget,
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
        self.setWindowIcon(QIcon("assets/master_icon.png"))

        self.initUI()
        load_wifi_networks(self.table)

    def initUI(self) -> None:
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Network Name", "Signal Strength"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only

        # ✨ Customize header
        header: QHeaderView | None = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(30)  # Set header height

        get_and_apply_styles(
            script_file=__file__, file="header.qss", set_content=header.setStyleSheet
        )

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
        self.table.setColumnWidth(0, 405)  # Fixed width for Network Name
        self.table.setColumnWidth(1, 150)  # Fixed width for Signal Strength
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )

        # 🛒 Disable vertical and horizontal scrollbars
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Apply custom styles
        get_and_apply_styles(
            script_file=__file__,
            file="wifi_table.qss",
            set_content=self.table.setStyleSheet,
        )

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)


def master():
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    master()
