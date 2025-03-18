# Built-in Modules
from typing import Literal

# PyQt6 Modules
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit


class TerminalAutoComplete(QLineEdit):
    def __init__(self, commands, parent=None) -> None:
        super().__init__(parent)
        self.commands: list = sorted(commands)  # Sort for consistency
        self.history: list = []  # Stores previously entered commands
        self.history_index = -1  # Position in history
        self.suggestion: Literal[""] = ""  # Stores the current suggestion
        self.match_index = -1  # Tracks cycling position

        self.textEdited.connect(self.show_suggestion)
        self.returnPressed.connect(self.store_history)

    def show_suggestion(self, text) -> None:
        """Update inline autocompletion when typing."""
        if not text:
            self.suggestion = ""
            return

        # Exact prefix match
        matches: list = [cmd for cmd in self.commands if cmd.startswith(text)]

        if matches:
            self.suggestion = matches[0]
            self.setText(self.suggestion)

            # Select the extra text
            self.setSelection(len(text), len(self.suggestion) - len(text))

            self.match_index = 0  # Reset cycling index
        else:
            self.suggestion = ""

    def keyPressEvent(self, event) -> None:
        """Handle Tab completion, History navigation, and Backspace."""
        key = event.key()

        if key == Qt.Key_Tab:
            matches: list = [
                cmd for cmd in self.commands if cmd.startswith(self.text())
            ] or self.fuzzy_match(self.text())
            if matches:
                # Cycle through matches
                self.match_index: int = (self.match_index + 1) % len(matches)

                self.suggestion = matches[self.match_index]
                self.setText(self.suggestion)
                self.setSelection(
                    len(self.text()), len(self.suggestion) - len(self.text())
                )
            return

        elif key == Qt.Key_Backspace:
            if self.hasSelectedText():
                # Remove only the suggested part
                self.setText(self.text()[: self.selectionStart()])
            else:
                super().keyPressEvent(event)  # Default behavior
            self.suggestion = ""
            return

        elif key == Qt.Key_Up:
            """Navigate command history (Up Arrow)"""
            if self.history:
                self.history_index: int = (self.history_index - 1) % len(self.history)
                self.setText(self.history[self.history_index])
                self.suggestion = ""
            return

        elif key == Qt.Key_Down:
            """Navigate command history (Down Arrow)"""
            if self.history:
                self.history_index: int = (self.history_index + 1) % len(self.history)
                self.setText(self.history[self.history_index])
                self.suggestion = ""
            return

        super().keyPressEvent(event)  # Default behavior

    def store_history(self) -> None:
        """Save commands in history when Enter is pressed."""
        text: str = self.text().strip()
        if text and text not in self.history:
            self.history.append(text)  # Store only unique commands
        self.history_index: int = len(self.history)  # Reset history index
        self.suggestion = ""
