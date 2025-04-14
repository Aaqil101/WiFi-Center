# Built-in Modules
import subprocess
import sys
import time
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

# Core Modules
from core.available_networks import open_wifi_manager
from core.wifi_connect import WiFiConnector
from core.wifi_disconnect import disconnect
from core.wifi_networks import load_wifi_networks

# Helpers Modules
from helpers import (
    Buttons,
    Icons,
    MessageBox,
    get_and_apply_styles,
    hibernate,
    hide_output_box_with_animation,
    lock_or_logout,
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
        self.wifi_connector = WiFiConnector()

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

        # Get current command (preserve original case for SSID)
        current_command: str = commands[index].strip()

        # Process current command
        if current_command.startswith("-c ") or current_command.startswith("connect "):
            command_result: bool = self.execute_command(current_command)
        else:
            command_result: bool = self.execute_command(current_command.lower())

        # If command uses animation, wait for animation to complete
        if current_command in ["-d", "disconnect"] or not command_result:
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
        command_lower: str = command.lower()

        msg_box = MessageBox(
            title="Confirmation",
            text="Are you sure?",
            fixed_size=(180, 125),
            icon_path=Path(__file__).parent.parent / "assets" / "lock_icon.png",
        )

        # Match other commands using the lowercase version
        if command_lower in ["-q", "cls", "quit", "exit", "close", "terminate"]:
            QApplication.quit()
            return True

        elif command_lower in ["-d", "disconnect"]:
            disconnect(self.window)
            return True

        elif command_lower in ["-r", "refresh"]:
            load_wifi_networks(self.window.table, force_refresh=True)
            return True

        elif command_lower in ["shutdown"]:
            if msg_box.show():
                shutdown()
                return True
            return False

        elif command_lower in ["reboot", "restart"]:
            if msg_box.show():
                reboot()
                return True
            return False

        elif command_lower == "sleep":
            if msg_box.show():
                sleep()
                return True
            return False

        elif command_lower in ["hibernate"]:
            if msg_box.show():
                hibernate()
                return True
            return False

        elif command_lower in ["lock", "logout"]:
            if msg_box.show():
                lock_or_logout()
                return True
            return False

        elif command_lower in ["-w", "wifi-manager"]:
            open_wifi_manager(terminal="cmd")
            return True

        elif command.startswith("-c ") or command.startswith("connect "):
            # Extract the SSID from the command
            parts: list[str] = command.split(" ", 1)
            if len(parts) == 2 and parts[1].strip():
                ssid: str = parts[1].strip()

                # Show processing animation
                processing(self.window, begin=True)

                # Prepare to connect using the WiFiConnector
                result: str = self.wifi_connector.process_input(f"connect={ssid}")

                # Display result in output box
                get_and_apply_styles(
                    script_file=Path(__file__).parent,
                    set_content_funcs={
                        (
                            "output_box_success.qss"
                            if "Successfully" in result
                            else "output_box_failure.qss"
                        ): self.window.output_box.setStyleSheet
                    },
                )
                self.window.output_box.setPlainText(result)

                # Show the output box with animation
                show_output_box_with_animation(self.window)

                # Hide the output box after 1.5 seconds and enable the command bar
                QTimer.singleShot(
                    1500, lambda: hide_output_box_with_animation(self.window)
                )
                QTimer.singleShot(1800, lambda: processing(self.window, end=True))

                return True
            else:
                # No SSID provided
                processing(self.window, begin=True)
                get_and_apply_styles(
                    script_file=Path(__file__).parent,
                    set_content_funcs={
                        "output_box_failure.qss": self.window.output_box.setStyleSheet
                    },
                )
                self.window.output_box.setPlainText(
                    "❌ No Wi-Fi network name provided. Usage: connect [NETWORK_NAME]"
                )

                # Show and hide with animation
                show_output_box_with_animation(self.window)
                QTimer.singleShot(
                    1500, lambda: hide_output_box_with_animation(self.window)
                )
                QTimer.singleShot(1800, lambda: processing(self.window, end=True))

                return False

        elif command_lower in ["-h", "--help"]:
            try:
                # Determine the full path to the script
                docs_app_path: Path = (
                    Path(__file__).parent.parent / "docs" / "docs_app.py"
                )

                if not docs_app_path.exists():
                    raise FileNotFoundError(f"docs_app.py not found at {docs_app_path}")

                # Start the script using the system's default Python interpreter
                subprocess.Popen(
                    [sys.executable, docs_app_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                # Wait a short time to ensure the process starts
                time.sleep(1)
            except Exception as e:
                start_msg_box = MessageBox(
                    title="Starting Error",
                    text=f"Error starting {e}",
                    fixed_size=(502, 131),
                    icon=Icons.Critical,
                    buttons=Buttons.Ok,
                )
                start_msg_box.show()
                raise

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
