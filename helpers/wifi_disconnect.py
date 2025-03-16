# Built-in Modules
import subprocess
from pathlib import Path

# PyQt6 Modules
from PyQt6.QtCore import QTimer

# Helpers Modules
from helpers import (
    get_and_apply_styles,
    hide_output_box_with_animation,
    processing,
    show_output_box_with_animation,
)


def disconnect(self) -> None:
    processing(self, begin=True)
    try:
        process: subprocess.CompletedProcess[str] = subprocess.run(
            ["netsh", "wlan", "disconnect"],
            shell=True,
            capture_output=True,
            text=True,
        )

        if process.returncode == 0:
            get_and_apply_styles(
                script_file=Path(__file__).parent,
                set_content_funcs={
                    "output_box_success.qss": self.output_box.setStyleSheet
                },
            )
            self.output_box.setPlainText("✅ Successfully disconnected from Wi-Fi.")
        else:
            get_and_apply_styles(
                script_file=__file__,
                set_content_funcs={
                    "output_box_failure.qss": self.output_box.setStyleSheet
                },
            )
            self.output_box.setPlainText(
                "❌ Failed to disconnect from Wi-Fi. Try running as administrator."
            )
    except subprocess.CalledProcessError as e:
        print(f"⚠ Error: {e}")

    # Show the output box with animation
    show_output_box_with_animation(self)

    # Hide the output box after 0.5 seconds and then enable the command bar
    QTimer.singleShot(500, lambda: hide_output_box_with_animation(self))

    # Enable the command bar after the hide animation is complete (1200ms total)
    QTimer.singleShot(1200, lambda: processing(self, end=True))
