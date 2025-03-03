import sys

from PyQt6.QtWidgets import QApplication, QTableView


class RoundedTableView(QTableView):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            """
            QTableView {
                background-color: #2D2D30;
                border: 1px solid #333340;
                border-radius: 12px;
                gridline-color: #333340;
            }

            QTableView::item {
                border-bottom: 1px solid #333340;
                padding: 5px;
            }

            QHeaderView::section {
                background-color: #2D2D30;
                color: white;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #333340;
                padding: 5px;
            }

            /* Handle corner widget between headers */
            QTableCornerButton::section {
                background-color: #2D2D30;
                border: none;
            }
        """
        )

        # Additional settings to improve appearance
        self.setFrameShape(QTableView.Shape.NoFrame)
        self.setShowGrid(False)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().setHighlightSections(False)


# Example usage
if __name__ == "__main__":
    app = QApplication(sys.argv)
    table = RoundedTableView()
    table.resize(600, 400)
    table.show()
    sys.exit(app.exec())
