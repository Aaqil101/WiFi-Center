# In-Build Modules
import subprocess
import sys

# PyQt6 Modules
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MasterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Wi-Fi Center")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon("assets/master_icon.png"))

        # Wifi Disconnect Button
        self.wifi_disconnect_button = QPushButton("Disconnect")
        self.wifi_disconnect_button.setFixedWidth(140)
        self.wifi_disconnect_button.setFixedHeight(40)
        self.wifi_disconnect_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }

            QPushButton:hover {
                background-color: #d32f2f;
            }

            QPushButton:pressed {
                background-color: #c62828;
                padding-left: 5px;
                padding-top: 5px;
            }
            """
        )
        self.wifi_disconnect_button.setToolTip(
            "Click to <b>disconnect</b> from the current Wi-Fi network"
        )
        self.wifi_disconnect_button.clicked.connect(self.disconnect_wifi)

        # Hidden Text Box
        self.output_box = QTextEdit()
        self.output_box.setFixedHeight(40)
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet(
            "background-color: #121212; color: lightgray; border: none;"
        )
        self.output_box.hide()

        # Layouts
        master_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        button_layout.addStretch()
        button_layout.addWidget(self.wifi_disconnect_button)

        master_layout.addStretch()
        master_layout.addLayout(button_layout)
        master_layout.addWidget(self.output_box)

        self.setLayout(master_layout)

    def disconnect_wifi(self):
        try:
            process = subprocess.run(
                ["netsh", "wlan", "disconnect"],
                shell=True,
                capture_output=True,
                text=True,
            )

            if process.returncode == 0:
                self.output_box.setPlainText("✅ Successfully disconnected from Wi-Fi.")
            else:
                self.output_box.setPlainText(
                    "❌ Failed to disconnect from Wi-Fi. Try running as administrator."
                )
        except subprocess.CalledProcessError as e:
            print(f"⚠ Error: {e}")

        self.show_output_box_with_animation()

        # Hide the output box after 1 seconds
        QTimer.singleShot(1000, self.hide_output_box_with_animation)

    def show_output_box_with_animation(self):
        self.output_box.show()

        # Fade-in animation
        self.fade_in_animation = QPropertyAnimation(self.output_box, b"windowOpacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Slide-in animation
        self.slide_in_animation = QPropertyAnimation(self.output_box, b"geometry")
        self.slide_in_animation.setDuration(500)
        start_rect = QRect(
            self.output_box.x(),
            self.height(),
            self.output_box.width(),
            self.output_box.height(),
        )
        end_rect = QRect(
            self.output_box.x(),
            self.height() - self.output_box.height(),
            self.output_box.width(),
            self.output_box.height(),
        )
        self.slide_in_animation.setStartValue(start_rect)
        self.slide_in_animation.setEndValue(end_rect)
        self.slide_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Start animations
        self.fade_in_animation.start()
        self.slide_in_animation.start()

    def hide_output_box_with_animation(self):
        # Fade-out animation
        self.fade_out_animation = QPropertyAnimation(self.output_box, b"windowOpacity")
        self.fade_out_animation.setDuration(500)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Slide-out animation
        self.slide_out_animation = QPropertyAnimation(self.output_box, b"geometry")
        self.slide_out_animation.setDuration(500)
        start_rect = QRect(
            self.output_box.x(),
            self.height() - self.output_box.height(),
            self.output_box.width(),
            self.output_box.height(),
        )
        end_rect = QRect(
            self.output_box.x(),
            self.height(),
            self.output_box.width(),
            self.output_box.height(),
        )
        self.slide_out_animation.setStartValue(start_rect)
        self.slide_out_animation.setEndValue(end_rect)
        self.slide_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Connect the end of the fade-out animation to hide the output box
        self.fade_out_animation.finished.connect(self.output_box.hide)

        # Start animations
        self.fade_out_animation.start()
        self.slide_out_animation.start()


def master():
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    master()
