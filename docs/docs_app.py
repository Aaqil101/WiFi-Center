# Built-in Modules
import sys
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtCore import QEvent, Qt, QUrl
from PyQt6.QtGui import QIcon, QKeyEvent, QKeySequence, QShortcut
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

if __name__ == "__main__":
    # Add the package root to the Python path
    sys.path.append(str(Path(__file__).parent.parent))

# Helpers Modules
from helpers import center_on_screen


class DocumentationWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Documentation")
        self.setGeometry(100, 100, 850, 710)

        icon_path: Path = Path(__file__).parent / "assets" / "documentation_icon.png"

        self.setWindowIcon(QIcon(str(icon_path)))

        # Initialize UI elements
        self.initUI()

    def initUI(self) -> None:
        # Html content display
        self.web_view = QWebEngineView()

        self.setStyleSheet(
            """
            background-color: rgb(31, 39, 56);
            """
        )

        # Get and apply styles
        self.style_dir: Path = Path(__file__).parent / "styles" / "styles.css"
        self.style_url: str = QUrl.fromLocalFile(str(self.style_dir)).toString()

        # Set default content and focus policy
        initial_file_path: Path = Path(__file__).parent / "index.html"
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
        # self.web_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.web_view)
        container.setLayout(layout)

        self.setCentralWidget(container)

        center_on_screen(self)

        # Add keyboard shortcuts
        self.setup_shortcuts()

    # Add this new method
    def setup_shortcuts(self) -> None:
        # ESC shortcut to close window
        close_shortcut = QShortcut(QKeySequence("Esc"), self)
        close_shortcut.activated.connect(self.close)


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
