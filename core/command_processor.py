# Built-in Modules
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

# Core Modules
from core.wifi_disconnect import disconnect
from core.wifi_networks import load_wifi_networks

# Helpers Modules
from helpers import (
    get_and_apply_styles,
    hibernate,
    hide_output_box_with_animation,
    lock_or_logout,
    msg_box,
    processing,
    reboot,
    show_output_box_with_animation,
    shutdown,
    sleep,
)


class CommandProcessor:
    def __init__(self, window) -> None:
        """
        Initialize the CommandProcessor with a reference to the main window.

        Args:
            window: Reference to the MasterWindow instance
        """
        self.window = window

    def process_input(self, input_text: str) -> None:
        """
        Process user input, handling command chaining with &&.

        Args:
            input_text (str): The text input from the command bar
        """
        # Parse commands and execute them sequentially
        commands: list[str] = input_text.split("&&")
        self._execute_command_chain(commands)

    def _execute_command_chain(self, commands: list[str], index: int = 0) -> None:
        """
        Execute commands sequentially with proper handling of animations.

        Args:
            commands (list[str]): List of commands to execute
            index (int): Current command index
        """
        # Base case: all commands processed
        if index >= len(commands):
            return

        # Get current command
        current_command: str = commands[index].strip().lower()

        # Process current command
        command_result: bool = self.execute_command(current_command)

        # If command uses animation, wait for animation to complete
        if current_command in ["d", "disconnect"] or not command_result:
            # For commands with animation or invalid commands, wait for animation to complete
            QTimer.singleShot(
                2000, lambda: self._execute_command_chain(commands, index + 1)
            )
        else:
            # For commands without animation, proceed immediately
            self._execute_command_chain(commands, index + 1)

    def execute_command(self, command: str) -> bool:
        """
        Execute a single command and return whether it was successful.

        Args:
            command (str): The command to execute

        Returns:
            bool: True if command executed successfully, False otherwise
        """
        if command in ["-q", "cls", "quit", "exit", "close", "terminate"]:
            QApplication.quit()
            return True

        elif command in ["-d", "disconnect"]:
            self.window.testing()
            # disconnect(self.window)
            return True

        elif command in ["-r", "refresh"]:
            load_wifi_networks(self.window.table, force_refresh=True)
            return True

        elif command in ["shutdown"]:
            if msg_box():
                shutdown()
                return True
            return False

        elif command in ["reboot", "restart"]:
            if msg_box():
                reboot()
                return True
            return False

        elif command == "sleep":
            if msg_box():
                sleep()
                return True
            return False

        elif command in ["hibernate"]:
            if msg_box():
                hibernate()
                return True
            return False

        elif command in ["lock", "logout"]:
            if msg_box():
                lock_or_logout()
                return True
            return False

        elif command in ["-c", "connect"]:
            print("Working on it...")
            return True

        elif command in ["-h", "--help"]:
            print("Working on it...")
            return True

        else:
            self._show_invalid_command_message()
            return False

    def _show_invalid_command_message(self) -> None:
        """Display the invalid command message with animation"""
        processing(self.window, begin=True)
        get_and_apply_styles(
            script_file=Path(__file__).parent,
            set_content_funcs={
                "output_box_failure.qss": self.window.output_box.setStyleSheet
            },
        )
        self.window.output_box.setPlainText(
            "❌ Invalid Command, Type '--help or -h' to see available commands."
        )

        # Show the output box with animation
        show_output_box_with_animation(self.window)

        # Hide the output box after 1.5 seconds and then enable the command bar
        QTimer.singleShot(1500, lambda: hide_output_box_with_animation(self.window))

        # Enable the command bar after the hide animation is complete (1800ms total)
        QTimer.singleShot(1800, lambda: processing(self.window, end=True))
