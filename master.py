# In-Build Modules
import subprocess
import sys

# PyQt6 Modules
from PyQt6.QtCore import (
    QAbstractTableModel,
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Helper Modules
from helper.window_effects import ApplyMica


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

        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Wi-Fi Center")
        self.setFixedSize(600, 400)
        self.setWindowIcon(QIcon("assets/master_icon.png"))

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        ApplyMica(self.winId())

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
        self.network_table.setFont(QFont("JetBrainsMono Nerd Font Propo"))
        self.network_table.setStyleSheet(
            """
            QTableView {
                gridline-color: rgb(100, 100, 100);
                color: rgb(255, 255, 255);
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QHeaderView::section {
                background-color: rgb(40, 40, 40);
                color: white;
                padding: 10px;
                font-size: 16px;
                font-weight: 1000;
                text-align: left;
            }
            /* Hide vertical scrollbar */
            QScrollBar:vertical {
                width: 0px;
                background: transparent;
            }
            QScrollBar:horizontal {
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
        self.network_table.setColumnWidth(0, 380)  # Network Name column
        self.network_table.setColumnWidth(1, 200)  # Signal Strength column
        self.network_table.horizontalHeader().setStretchLastSection(False)
        self.network_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.network_table.setEditTriggers(
            QTableView.EditTrigger.NoEditTriggers
        )  # Make table read-only
        self.network_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )  # Hide vertical scrollbar

        # Hidden Text Box
        self.output_box = QTextEdit()
        self.output_box.setFixedHeight(40)
        self.output_box.setFixedWidth(580)
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet(
            """
            QTextEdit {
                background-color: rgb(0, 0, 0);
                color: rgb(255, 255, 255);
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
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
        self.command_bar.setPlaceholderText("Type here...")
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
        master_layout.setContentsMargins(10, 10, 10, 10)  # Set consistent margins
        master_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Center align table
        table_layout = QHBoxLayout()
        table_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_layout.addWidget(self.network_table)

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

        if "d" in user_input.lower():
            self.disconnect_wifi()

        if "q" in user_input.lower():
            QApplication.quit()

    def disconnect_wifi(self) -> None:
        try:
            process = subprocess.run(
                ["netsh", "wlan", "disconnect"],
                shell=True,
                capture_output=True,
                text=True,
            )

            if process.returncode == 0:
                self.output_box.setPlainText("✅ Successfully disconnected from Wi-Fi.")
            else:
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
        self.output_box.show()

        # Get the center position
        center_x = (self.width() - self.output_box.width()) // 2

        # Set initial position and size for the output box
        self.output_box.setGeometry(
            center_x,  # Center horizontally
            self.network_table.y()
            + self.network_table.height()
            + 5,  # Just below table
            580,  # Fixed width to match other elements
            40,  # Fixed height
        )

        # Fade-in animation
        self.fade_in_animation = QPropertyAnimation(self.output_box, b"windowOpacity")
        self.fade_in_animation.setDuration(400)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Slide-in animation
        self.slide_in_animation = QPropertyAnimation(self.output_box, b"geometry")
        self.slide_in_animation.setDuration(400)

        # Calculate start and end positions
        start_rect = QRect(
            center_x,
            self.network_table.y()
            + self.network_table.height()
            + 45,  # Start below visible area
            580,
            40,
        )
        end_rect = QRect(
            center_x,
            self.network_table.y() + self.network_table.height() + 5,  # End position
            580,
            40,
        )

        self.slide_in_animation.setStartValue(start_rect)
        self.slide_in_animation.setEndValue(end_rect)
        self.slide_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Start animations
        self.fade_in_animation.start()
        self.slide_in_animation.start()

    def hide_output_box_with_animation(self) -> None:
        # Get the center position
        center_x = (self.width() - self.output_box.width()) // 2

        # Fade-out animation
        self.fade_out_animation = QPropertyAnimation(self.output_box, b"windowOpacity")
        self.fade_out_animation.setDuration(400)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Slide-out animation
        self.slide_out_animation = QPropertyAnimation(self.output_box, b"geometry")
        self.slide_out_animation.setDuration(400)

        # Calculate start and end positions
        start_rect = QRect(
            center_x,
            self.network_table.y()
            + self.network_table.height()
            + 5,  # Current position
            580,
            40,
        )
        end_rect = QRect(
            center_x,
            self.network_table.y()
            + self.network_table.height()
            + 45,  # End position (out of view)
            580,
            40,
        )

        self.slide_out_animation.setStartValue(start_rect)
        self.slide_out_animation.setEndValue(end_rect)
        self.slide_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Connect the end of the fade-out animation to hide the output box
        self.fade_out_animation.finished.connect(self.output_box.hide)

        # Start animations
        self.fade_out_animation.start()
        self.slide_out_animation.start()

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


def master():
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    window.command_bar.setFocus()
    sys.exit(app.exec())


if __name__ == "__main__":
    master()
