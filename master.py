# In-Build Modules
import subprocess
import sys

# PyQt6 Modules
from PyQt6.QtCore import QAbstractTableModel, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QRegion
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Helper Modules
from helper import GlobalBlur


class WiFiTableModel(QAbstractTableModel):
    """Custom Table Model to manage Wi-Fi network data."""

    def __init__(self, networks=None) -> None:
        super().__init__()
        self.headers: list[str] = ["Network", "Strength"]
        self.networks = networks or []

    def rowCount(self, index=None) -> int:
        return len(self.networks)

    def columnCount(self, index=None) -> int:
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row: int = index.row()
        col: int = index.column()

        if role == Qt.ItemDataRole.DisplayRole:  # Display text
            return self.networks[row][col]

        return None

    def headerData(
        self, section, orientation, role=Qt.ItemDataRole.DisplayRole
    ) -> str | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]
        return None

    def update_data(self, new_data) -> None:
        """Updates table data dynamically."""
        self.beginResetModel()
        self.networks = new_data
        self.endResetModel()


class MasterWindow(QWidget):
    """Main application window for Wi-Fi Center."""

    def __init__(self) -> None:
        super().__init__()

        # Get the hWnd of your window
        hwnd: int = self.winId().__int__()

        # Make window background translucent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Blur the window
        GlobalBlur(HWND=hwnd, hexColor=False, Acrylic=True, Dark=True)

        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Wi-Fi Center")
        self.setFixedSize(600, 400)
        self.setWindowIcon(QIcon("assets/master_icon.png"))

        # Table View
        self.model = WiFiTableModel()
        self.model.headers = [
            "Network",
            "Strength",
        ]
        self.network_table = QTableView()
        self.network_table.setModel(self.model)
        self.network_table.setFixedWidth(580)
        self.network_table.setFixedHeight(290)
        self.network_table.setFont(QFont("Verdana"))

        # Table View styling sheet
        self.network_table.setStyleSheet(
            """
            QTableView {
                gridline-color: rgb(100, 100, 100);
                color: rgb(255, 255, 255);
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                border: 3px solid rgb(60, 60, 60);
                outline: none;
            }
            QTableView::item {
                border: none;
                border-bottom: 1px solid rgb(60, 60, 60);
                padding: 5px;
            }
            QHeaderView::section {
                background-color: rgba(60, 60, 60, 0);
                color: white;
                padding: 10px;
                font-size: 16px;
                font-weight: 1000;
                text-align: center;
                border: none;
                border-bottom: 1px solid rgb(60, 60, 60);
            }
            QTableCornerButton::section {
                background: transparent;
                border: none;
            }
            /* Remove grid lines by setting them transparent */
            QTableView::item:selected {
                background-color: rgba(100, 100, 100, 70);
                color: white;
            }
            /* Hide scrollbars */
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
                background: transparent;
            }
            """
        )

        self.network_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.network_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self.network_table.setColumnWidth(0, 380)
        self.network_table.setColumnWidth(1, 200)
        self.network_table.horizontalHeader().setStretchLastSection(False)

        # Hide row numbers
        self.network_table.verticalHeader().setVisible(False)

        # Disable user interaction
        self.network_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        # Make table read-only
        self.network_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        # Hide vertical scrollbar
        self.network_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.table_frame = QFrame()
        self.table_frame.setFixedWidth(580)
        self.table_frame.setFixedHeight(290)
        self.table_frame.setStyleSheet(
            """
            QFrame {
                border-radius: 10px;
                background-color: rgba(40, 45, 50, 0);
            }
            """
        )

        # Create a layout for the frame
        frame_layout = QVBoxLayout(self.table_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self.network_table)

        def paintEvent(self, event) -> None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Set up rounded region for the table
            region = QRegion(
                self.network_table.geometry(), QRegion.RegionType.Rectangle
            )
            self.network_table.setMask(region)

            super().paintEvent(event)

        # Hidden Text Box
        self.output_box = QTextEdit()
        self.output_box.setFixedHeight(40)
        self.output_box.setFixedWidth(580)
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont("Times New Roman"))

        # Hidden Text Box styling sheet
        self.output_box.setStyleSheet(
            """
            QTextEdit {
                background-color: rgba(40, 45, 50, 180);
                color: rgb(255, 255, 255);
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: 600;
                border: 1px solid rgba(60, 60, 60, 180);
            }
            /* Hide all scrollbars */
            QScrollBar {
                width: 0px;
                height: 0px;
                background: transparent;
            }
            """
        )

        self.output_box.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.output_box.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.output_box.hide()

        # Command Bar
        self.command_bar = QLineEdit()
        self.command_bar.setFixedWidth(580)
        self.command_bar.setFixedHeight(40)
        self.command_bar.setFont(QFont("Garamond"))
        # self.command_bar.setPlaceholderText("Type here...")
        self.command_bar.setStyleSheet(
            """
            QLineEdit {
                background-color: rgb(255, 255, 255);
                color: rgb(0, 0, 0);
                border-radius: 5px;
                padding-left: 15px;
                padding-right: 15px;
                font-size: 18px;
            }
            """
        )
        self.command_bar.returnPressed.connect(self.check_input)

        # Layouts - Adjust to center align all elements
        master_layout = QVBoxLayout()
        master_layout.setContentsMargins(10, 10, 10, 10)
        master_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Center align table
        table_layout = QHBoxLayout()
        table_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_layout.addWidget(self.table_frame)

        # Center align output box
        output_layout = QHBoxLayout()
        output_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        output_layout.addWidget(self.output_box)

        # Center align command bar
        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.command_bar)

        master_layout.addLayout(table_layout)
        master_layout.addLayout(output_layout)
        master_layout.addStretch()
        master_layout.addLayout(input_layout)

        self.setLayout(master_layout)

        # Show available networks on startup
        self.show_available_networks()

    def check_input(self):
        user_input: str = self.command_bar.text()
        self.command_bar.clear()

        # Disconnect
        if "d" in user_input.lower():
            self.disconnect_wifi()

        # Quit
        if "q" in user_input.lower():
            QApplication.quit()

        # Open Wi-Fi Hub
        if "o" in user_input.lower():
            self.open_wifi_hub()

    def disconnect_wifi(self) -> None:
        try:
            process = subprocess.run(
                ["netsh", "wlan", "disconnect"],
                shell=True,
                capture_output=True,
                text=True,
            )

            if process.returncode == 0:
                self.output_box.setTextColor(QColor(37, 215, 127))
                self.output_box.setPlainText("✅ Successfully disconnected from Wi-Fi.")
            else:
                self.output_box.setTextColor(QColor(249, 47, 96))
                self.output_box.setPlainText(
                    "❌ Failed to disconnect from Wi-Fi. Try running as administrator."
                )
        except subprocess.CalledProcessError as e:
            print(f"⚠ Error: {e}")

        # Show the output box with animation
        self.show_output_box_with_animation()

        # Hide the output box after 2 seconds
        QTimer.singleShot(2000, self.hide_output_box_with_animation)

    def show_output_box_with_animation(self) -> None:
        """Display the output box without animation."""
        # Get the center position
        center_x: int = (self.width() - self.output_box.width()) // 2

        # Set fixed position for the output box
        self.output_box.setGeometry(
            center_x,  # Center horizontally
            self.network_table.y()
            + self.network_table.height()
            + 4,  # Just below table
            580,  # Fixed width
            40,  # Fixed height
        )

        # Simply show the widget
        self.output_box.show()

    def hide_output_box_with_animation(self) -> None:
        self.output_box.hide()

    def show_available_networks(self) -> None:
        try:
            process = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                shell=True,
                capture_output=True,
                text=True,
            )

            if process.returncode == 0:
                output: str = process.stdout
                networks = self.parse_networks(output)
                self.model.update_data(networks)
            else:
                self.output_box.setTextColor(QColor(249, 47, 96))
                self.output_box.setPlainText(
                    "❌ Failed to retrieve available networks. Try running as administrator."
                )
                self.output_box.show()
        except subprocess.CalledProcessError as e:
            print(f"⚠ Error: {e}")

    def parse_networks(self, output: str) -> list:
        """Parses Wi-Fi networks from netsh output."""
        networks = []
        lines: list[str] = output.split("\n")
        current_network = None

        for line in lines:
            if "SSID" in line:
                if current_network:
                    networks.append(current_network)
                current_network: list[str] = [
                    line.split(":")[1].strip(),
                    "",
                ]  # Name, Signal Placeholder
            elif "Signal" in line and current_network:
                current_network[1] = line.split(":")[1].strip()  # Signal Strength

        if current_network:
            networks.append(current_network)

        return networks

    def open_wifi_hub(self) -> None:
        try:
            process = subprocess.run(
                ["cmd", "/c", "start", "ms-availablenetworks:///"],
                shell=True,
                capture_output=True,
                text=True,
            )

            if process.returncode == 0:
                self.output_box.setTextColor(QColor(37, 215, 127))
                self.output_box.setPlainText("✅ Successfully opened Wi-Fi Hub.")
            else:
                self.output_box.setTextColor(QColor(249, 47, 96))
                self.output_box.setPlainText("❌ Failed to open Wi-Fi Hub.")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Error: {e}")

        # Show the output box with animation
        self.show_output_box_with_animation()

        # Hide the output box after 1 seconds
        QTimer.singleShot(1000, self.hide_output_box_with_animation)


def master():
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    window.command_bar.setFocus()
    sys.exit(app.exec())


if __name__ == "__main__":
    master()
