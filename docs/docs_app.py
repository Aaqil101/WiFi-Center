# Built-in Modules
import sys
from pathlib import Path

# QtAwesome Modules
import qtawesome as qta

# PyQt6 Modules
from PyQt6.QtCore import QRect, QSize, Qt, QUrl
from PyQt6.QtGui import QColor, QFont, QIcon, QKeyEvent, QRegion
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

if __name__ == "__main__":
    # Add the package root to the Python path
    sys.path.append(str(Path(__file__).parent.parent))

# Helpers Modules
from helpers import center_on_screen, get_and_apply_styles


class DocumentationWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Documentation")
        self.setGeometry(100, 100, 850, 750)

        icon_path: Path = Path(__file__).parent / "assets" / "documentation_icon.png"

        self.setWindowIcon(QIcon(str(icon_path)))

        # Initialize UI elements
        self.initUI()

        # Populate topics list from files
        self.populate_topics()

    def initUI(self) -> None:
        # Create widgets
        self.search_bar = QLineEdit()  # Search bar
        self.topic_list = QListWidget()  # List of topics
        self.web_view = QWebEngineView()  # Html content display

        # Toggle sidebar
        self.toggle_button = QPushButton(qta.icon("mdi.dock-left"), "")

        self.topic_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Get and apply styles
        self.style_dir: Path = Path(__file__).parent / "website" / "styles.css"
        self.style_url: str = QUrl.fromLocalFile(str(self.style_dir)).toString()

        # Set default content and focus policy
        initial_file_path: Path = (
            Path(__file__).parent / "website" / "introduction.html"
        )
        if initial_file_path.exists():
            self.web_view.setUrl(QUrl.fromLocalFile(str(initial_file_path)))
        else:
            self.web_view.setHtml(
                f"""
                <html>
                <head>
                    <link rel="stylesheet" href="{self.style_url}">
                </head>
                <body>
                    <h1>Welcome to Documentation</h1>
                    <hr>
                    <p>Please select a topic from the list.</p>
                    <button onclick="window.location.href = 'introduction.html';">Go to Introduction</button>
                    <br>
                    <button onclick="window.location.href = 'installation.html';">Go to Installation</button>
                    <br>
                    <button onclick="window.location.href = 'usage.html';">Go to Usage</button>
                    <br>
                    <button onclick="window.location.href = 'basic_features.html';">Go to Basic Features</button>
                    <br>
                    <button onclick="window.location.href = 'advanced_features.html';">Go to Advanced Features</button>
                    <br>
                    <button onclick="window.location.href = 'troubleshooting.html';">Troubleshooting</button>
                    <br>
                    <button onclick="window.location.href = 'faq.html';">FAQ</button>
                </body>
                </html>
                """,
                QUrl.fromLocalFile(str(Path(__file__).parent / "website")),
            )
        self.web_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Set placeholder text for search bar
        self.search_bar.setPlaceholderText("Search topics...")
        self.search_bar.setToolTip("Type a keyword to search help topics.")

        # Button tooltip, click event and focus policy
        self.toggle_button.setToolTip("Toggle Sidebar (Ctrl+S)")
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.toggle_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Connect topic selection to page navigation
        self.topic_list.itemClicked.connect(self.load_topic)
        self.search_bar.textChanged.connect(self.filter_topics)

        # Layout for search bar + button
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove margins for a seamless look
        search_layout.addWidget(self.toggle_button)
        search_layout.addWidget(self.search_bar)

        # Wrap in a QWidget for correct layout behavior
        search_widget = QWidget()
        search_widget.setLayout(search_layout)

        # Setup layout with reduced margins
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(search_widget)
        left_layout.addWidget(self.topic_list)
        left_panel.setLayout(left_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(self.web_view)
        splitter.setSizes([135, 600])

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(splitter)
        container.setLayout(layout)

        self.setCentralWidget(container)

        # Store reference for toggling sidebar
        self.left_panel: QWidget = left_panel

        get_and_apply_styles(
            script_file=__file__,
            set_content_funcs={
                "background.qss": self.setStyleSheet,
                "splitter.qss": splitter.setStyleSheet,
                "search_bar.qss": self.search_bar.setStyleSheet,
                "topic_list.qss": self.topic_list.setStyleSheet,
                "toggle_button.qss": self.toggle_button.setStyleSheet,
            },
        )

        center_on_screen(self)

    def toggle_sidebar(self) -> None:
        """Toggle the visibility of the search bar and topic list."""
        is_visible: bool = self.left_panel.isVisible()
        self.left_panel.setVisible(not is_visible)

    def populate_topics(self) -> None:
        """Populate topic list with section headers"""
        self.topic_list.clear()

        # Add headers and topics
        self.add_section_header("Getting Started")
        self.topic_list.addItem("Introduction")
        self.topic_list.addItem("Installation")

        self.add_section_header("Features")
        self.topic_list.addItem("Basic Features")
        self.topic_list.addItem("Advanced Features")

        self.add_section_header("Other")
        self.topic_list.addItem("Troubleshooting")
        self.topic_list.addItem("FAQ")

    def add_section_header(self, text) -> None:
        """Add a fully customized non-selectable section header to the list"""
        item = QListWidgetItem(text)

        # Make the item non-selectable by disabling all interactive flags
        item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled)

        # Text color
        item.setForeground(QColor("#4682B4"))

        # Font customization
        font: QFont = item.font()
        font.setBold(True)

        # Increase font size by 2 points
        font.setPointSize(font.pointSize() + 2)

        # Set font family
        font.setFamily("Segoe UI")

        item.setFont(font)

        # Add padding with a custom size hint
        item.setSizeHint(QSize(item.sizeHint().width(), item.sizeHint().height() + 10))

        # Add a custom role to identify this as a header
        item.setData(Qt.ItemDataRole.UserRole, "header")

        self.topic_list.addItem(item)

    def filter_topics(self, text) -> None:
        """Filter topics based on search text"""
        for i in range(self.topic_list.count()):
            item: QListWidgetItem | None = self.topic_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def load_topic(self, item) -> None:
        """Load a specific topic HTML file if the item is not a header"""
        # Path to topic HTML files
        self.website_dir: Path = Path(__file__).parent / "website"

        # Skip if this is a header item
        if item.data(Qt.ItemDataRole.UserRole) == "header":
            return

        topic_name = item.text()
        filename = topic_name.lower().replace(" ", "_") + ".html"
        file_path = self.website_dir / filename

        if file_path.exists():
            self.web_view.setUrl(QUrl.fromLocalFile(str(file_path)))
        else:
            self.web_view.setHtml(
                f"""
                <html>

                <head>
                    <link rel="stylesheet" href="{self.style_url}">
                </head>

                <body>
                    <h1>Topic Not Found</h1>
                    <hr>
                    <p>The file for '{topic_name}' was not found.</p>
                </body>

                </html>
                """,
                QUrl.fromLocalFile(str(Path(__file__).parent / "website")),
            )

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handles key press events for shortcuts."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current_item: QListWidgetItem = self.topic_list.currentItem()
            if current_item:
                self.load_topic(current_item)
        elif (
            event.key() == Qt.Key.Key_S
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.toggle_sidebar()
            self.search_bar.setFocus()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def main() -> None:
    from PyQt6.QtCore import QElapsedTimer

    timer = QElapsedTimer()
    timer.start()  # Start timing

    app = QApplication(sys.argv)
    window = DocumentationWindow()
    window.search_bar.setFocus()
    window.show()

    elapsed_time: float = timer.elapsed() / 1000  # Convert to seconds
    print(f"Launch time: {elapsed_time:.4f} seconds")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
