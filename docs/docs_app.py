# Built-in Modules
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

# PyQt6 Modules
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtWebEngineCore import QWebEnginePage
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
        self.setGeometry(100, 100, 1100, 700)

        icon_path: Path = (
            Path(__file__).parent / "assets" / "icons" / "documentation_icon.png"
        )

        self.setWindowIcon(QIcon(str(icon_path)))

        # Initialize UI elements
        self.initUI()

    def initUI(self) -> None:
        # Html content display
        self.web_view = QWebEngineView()

        # Create a custom page to handle link navigation
        self.custom_page = CustomWebPage(self.web_view)
        self.web_view.setPage(self.custom_page)

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


class CustomWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame) -> bool:
        url_string = url.toString()

        # For navigation by clicking on links
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            # Determine if this is an internal or external link
            parsed_url = urlparse(url_string)

            # Check if it's a local file or an external URL
            if parsed_url.scheme in ("http", "https") and not url_string.startswith(
                "file:"
            ):
                # Open external links in default browser
                webbrowser.open(url_string)
                return False
            # Allow navigation to local documentation files
            return True

        # Allow other navigation requests (initial page load, etc.)
        return super().acceptNavigationRequest(url, _type, isMainFrame)


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
