import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class KomoGUIStyle(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KomoGUI")
        self.setMinimumSize(700, 500)

        # Set dark theme
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background-color: #1a1b26;
                color: #ffffff;
            }
            QPushButton {
                background-color: #1a1b26;
                color: #aaaaaa;
                border: none;
                text-align: left;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2d2d40;
                color: #ffffff;
            }
            QFrame#sidebar {
                background-color: #1a1b26;
                border-right: 1px solid #333340;
            }
            QFrame#bottom_frame {
                background-color: #1a1b26;
                border-top: 1px solid #333340;
            }
        """
        )

        # Main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central_widget)

        # Create sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(150)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Add menu items to sidebar
        menu_items = [
            "General",
            "Animation",
            "Borders",
            "Stackbar",
            "Transparency",
            "Ignore Rules",
            "Workspaces",
        ]

        for item in menu_items:
            btn = QPushButton(item)
            sidebar_layout.addWidget(btn)

        # Add bottom sidebar buttons
        load_config_btn = QPushButton("Load Config")
        save_config_btn = QPushButton("Save Config")
        about_btn = QPushButton("About")
        sidebar_layout.addWidget(load_config_btn)
        sidebar_layout.addWidget(save_config_btn)
        sidebar_layout.addWidget(about_btn)

        # Create content area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add logo (you would need to create or obtain a watermelon logo)
        logo_label = QLabel()
        # Placeholder for the watermelon logo - in a real app, use an actual image
        logo_label.setFixedSize(100, 100)
        logo_label.setStyleSheet("background-color: transparent;")

        # Add title and instructions
        title_label = QLabel("KomoGUI")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        instruction_label = QLabel(
            "Load a configuration file to begin configuring your tiling world."
        )
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setFont(QFont("Arial", 12))
        instruction_label.setStyleSheet("color: #aaaaaa;")

        # Add widgets to content layout
        content_layout.addWidget(logo_label)
        content_layout.addWidget(title_label)
        content_layout.addSpacing(10)
        content_layout.addWidget(instruction_label)

        # Add sidebar and content to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)


def main():
    app = QApplication(sys.argv)
    window = KomoGUIStyle()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
