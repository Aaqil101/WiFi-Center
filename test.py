from PyQt6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout

class TableWidgetExample(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Table Example")
        self.setGeometry(100, 100, 500, 300)

        # Create table
        self.table = QTableWidget(self)
        self.table.setRowCount(3)  # Number of rows
        self.table.setColumnCount(3)  # Number of columns
        self.table.setHorizontalHeaderLabels(["Name", "Age", "City"])

        # Add data to the table
        data = [
            ("Alice", "25", "New York"),
            ("Bob", "30", "Los Angeles"),
            ("Charlie", "22", "Chicago")
        ]

        for row, (name, age, city) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(age))
            self.table.setItem(row, 2, QTableWidgetItem(city))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

# Run Application
app = QApplication([])
window = TableWidgetExample()
window.show()
app.exec()
