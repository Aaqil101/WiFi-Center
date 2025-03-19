# Built-in Modules
import sys
from pathlib import Path
from typing import Any

# PyQt6 Modules
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

if __name__ == "__main__":
    # Add the package root to the Python path
    sys.path.append(str(Path(__file__).parent.parent))

# Helpers Modules
from helpers import center_on_screen


class DocumentationWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Documentation")
        self.setGeometry(100, 100, 800, 600)

        icon_path: Path = Path(__file__).parent / "assets" / "documentation_icon.png"

        self.setWindowIcon(QIcon(str(icon_path)))

        self.initUI()

    def initUI(self) -> None:
        # Create widgets
        self.search_bar = QLineEdit()  # Search bar
        self.topic_list = QListWidget()  # List of topics
        self.help_content = QTextBrowser()  # Markdown content display

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: rgb(31, 39, 56)
            }
            """
        )

        self.topic_list.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(255, 255, 255, 0.04);
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 700;
                font-style: normal;
                font-family: "Trebuchet MS", "Lucida Sans Unicode", "Lucida Grande",
                    "Lucida Sans", Arial, sans-serif;
                padding: 4px;
                border: none;
                border-radius: 4px;
            }

            QListWidget:focus {
                background-color: #222;
                border-bottom: 2px solid #0078d7;
                border-right: 2px solid #0078d7;
                font-style: unset;
            }
            """
        )

        # Set placeholder text for search bar
        self.search_bar.setPlaceholderText("Search topics...")
        self.search_bar.setToolTip("Type a keyword to search help topics.")
        self.help_content.setOpenExternalLinks(True)  # Allow clicking on links

        self.help_content.setStyleSheet(
            """
            QTextBrowser {
                background-color: rgba(255, 255, 255, 0.04);
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 700;
                font-style: normal;
                font-family: "Trebuchet MS", "Lucida Sans Unicode", "Lucida Grande",
                    "Lucida Sans", Arial, sans-serif;
                padding: 4px;
                border: none;
                border-radius: 4px;
            }

            QTextBrowser:focus {
                background-color: #222;
                border-bottom: 2px solid #0078d7;
                border-right: 2px solid #0078d7;
                font-style: unset;
            }
            """
        )

        self.search_bar.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.04);
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 700;
                font-style: normal;
                font-family: "Trebuchet MS", "Lucida Sans Unicode", "Lucida Grande",
                    "Lucida Sans", Arial, sans-serif;
                padding: 4px;
                border: none;
                border-radius: 4px;
            }

            QLineEdit:focus {
                background-color: #222;
                border-bottom: 2px solid #0078d7;
                border-right: 2px solid #0078d7;
                font-style: unset;
            }
            """
        )

        # Connect search and navigation functionality
        self.search_bar.textChanged.connect(self.filter_topics)
        self.topic_list.itemClicked.connect(self.display_help)

        html: Path = Path(__file__).parent / "help.html"
        css_file: Path = Path(__file__).parent / "styles.css"

        # Load help content from HTML
        self.html_content: dict = self.load_help_content(html)
        self.populate_topics()

        # Load CSS if available
        self.apply_css(css_file)

        # Connect signals
        self.topic_list.itemClicked.connect(self.display_help)

        # Setup layout with reduced margins
        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: rgb(31, 39, 56);
            }

            QSplitter::handle:horizontal {
                background-color: rgb(31, 39, 56);
            }
            """
        )

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.topic_list)
        left_panel.setLayout(left_layout)

        # Set stretch factors for consistent sizing
        splitter.addWidget(left_panel)
        splitter.addWidget(self.help_content)
        splitter.setSizes([125, 600])

        # Ensure consistent splitter handling
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        # Main container with no margins
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # Remove container margins
        layout.addWidget(splitter)
        container.setLayout(layout)

        self.setCentralWidget(container)

        center_on_screen(self)

    def load_help_content(self, filename) -> dict:
        """Read the HTML file and extract topic sections."""
        with open(filename, "r", encoding="utf-8") as file:
            html_data: str = file.read()

        # Extract topics from <h2> tags
        import re

        topics: dict = {}
        matches: list[Any] = re.findall(r'<h2 id="(.*?)">(.*?)</h2>', html_data)
        for topic_id, topic_name in matches:
            start: int = html_data.index(f'<h2 id="{topic_id}">')
            end: int = html_data.find("<h2 id=", start + 1)
            topics[topic_name] = (
                html_data[start:end] if end != -1 else html_data[start:]
            )

        return topics

    def apply_css(self, css_file) -> None:
        """Apply external CSS styling to the markdown viewer."""
        if css_file.exists():
            with css_file.open("r", encoding="utf-8") as file:
                css: Any = file.read()
                self.help_content.setStyleSheet(css)

    def populate_topics(self) -> None:
        """Populate the topic list."""
        self.topic_list.clear()
        for topic in self.html_content.keys():
            self.topic_list.addItem(topic)

    def filter_topics(self, text) -> None:
        """Filter topics based on search input."""
        self.topic_list.clear()
        for topic in self.html_content.keys():
            if text.lower() in topic.lower():
                self.topic_list.addItem(topic)

    def display_help(self, item) -> None:
        """Display the selected help content."""
        topic: Any = item.text()
        self.help_content.setHtml(
            self.html_content.get(topic, "<b>No content available.</b>")
        )

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events for shortcuts.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def main() -> None:
    from PyQt6.QtCore import QElapsedTimer

    timer = QElapsedTimer()
    timer.start()  # Start timing

    app = QApplication(sys.argv)
    window = DocumentationWindow()
    window.show()

    elapsed_time: float = timer.elapsed() / 1000  # Convert to seconds
    print(f"Launch time: {elapsed_time:.4f} seconds")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
