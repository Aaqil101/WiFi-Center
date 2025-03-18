from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget


class TerminalAutoComplete(QLineEdit):
    def __init__(self, commands, parent=None):
        super().__init__(parent)
        self.commands = sorted(commands)  # Sort for consistency
        self.suggestion = ""  # Store the current suggestion
        self.match_index = -1  # Track cycling position

        self.textEdited.connect(self.show_suggestion)
        self.returnPressed.connect(self.clear_suggestion)

    def show_suggestion(self, text):
        """Update inline autocompletion when typing."""
        if not text:
            self.suggestion = ""
            return

        # Find all matches
        matches = [cmd for cmd in self.commands if cmd.startswith(text)]

        if matches:
            self.suggestion = matches[0]  # Take the first match
            self.setText(self.suggestion)
            self.setSelection(
                len(text), len(self.suggestion) - len(text)
            )  # Select the extra text
            self.match_index = 0  # Reset cycling index
        else:
            self.suggestion = ""

    def keyPressEvent(self, event):
        """Handle Tab completion, Backspace, and Enter."""
        key = event.key()

        if key == 9:  # Tab Key
            matches = [cmd for cmd in self.commands if cmd.startswith(self.text())]
            if matches:
                self.match_index = (self.match_index + 1) % len(
                    matches
                )  # Cycle through matches
                self.suggestion = matches[self.match_index]
                self.setText(self.suggestion)
                self.setSelection(
                    len(self.text()), len(self.suggestion) - len(self.text())
                )
            return

        elif key == 16777219:  # Backspace Key
            if self.hasSelectedText():
                self.setText(
                    self.text()[: self.selectionStart()]
                )  # Remove only suggested part
            else:
                super().keyPressEvent(event)  # Normal behavior
            self.suggestion = ""
            return

        super().keyPressEvent(event)  # Pass other keys to default behavior

    def clear_suggestion(self):
        """Clear the suggestion when Enter is pressed."""
        self.suggestion = ""
        self.setSelection(0, 0)  # Remove selection


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.command_bar = TerminalAutoComplete(
            ["disconnect", "shutdown", "debug", "deploy"]
        )
        layout.addWidget(self.command_bar)

        self.setLayout(layout)


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
