# Built-in Modules
import sys
from pathlib import Path

# Markdown Module
import markdown

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

        # Set placeholder text for search bar
        self.search_bar.setPlaceholderText("Search topics...")
        self.search_bar.setToolTip("Type a keyword to search help topics.")
        self.help_content.setOpenExternalLinks(True)  # Allow clicking on links

        # Connect search and navigation functionality
        self.search_bar.textChanged.connect(self.filter_topics)
        self.topic_list.itemClicked.connect(self.display_help)

        # Load help topics from markdown files
        self.topics = self.load_help_content()
        self.populate_topics()

        # Connect signals
        self.topic_list.itemClicked.connect(self.display_help)

        # Setup layout with reduced margins
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.topic_list)
        left_panel.setLayout(left_layout)

        # Set stretch factors for consistent sizing
        splitter.addWidget(left_panel)
        splitter.addWidget(self.help_content)
        splitter.setSizes([200, 600])

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

    def load_help_content(self):
        """Load all markdown files from the help directory."""
        # Directory containing markdown files
        self.help_dir: Path = Path(__file__).parent / "markdown"
        topics = {}

        if not self.help_dir.exists():
            print(f"Help directory '{self.help_dir}' not found!")
            return topics

        # Use Pathlib's glob() to find .md files
        for md_file in self.help_dir.glob("*.md"):
            topic_name: str = md_file.stem.replace("_", " ").title()
            with md_file.open("r", encoding="utf-8") as file:
                topics[topic_name] = markdown.markdown(file.read())

        return topics

    def populate_topics(self) -> None:
        """Populate the topic list."""
        self.topic_list.clear()
        for topic in self.topics.keys():
            self.topic_list.addItem(topic)

    def filter_topics(self, text) -> None:
        """Filter topics based on search input."""
        self.topic_list.clear()
        for topic in self.topics.keys():
            if text.lower() in topic.lower():
                self.topic_list.addItem(topic)

    def display_help(self, item) -> None:
        """Display the selected help content."""
        topic = item.text()
        self.help_content.setHtml(
            self.topics.get(topic, "<b>No content available.</b>")
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
