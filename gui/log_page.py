from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton
)

class LogPage(QWidget):

    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Date", "Category", "Amount", "Payment", "Rebate"]
        )
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

    def load_data(self):
        expenses = self.tracker.get_all_expenses()
        self.table.setRowCount(len(expenses))

        print(type(expenses))
        print(expenses)


        for row, exp in enumerate(expenses):
            self.table.setItem(row, 0, QTableWidgetItem(exp.id))
            self.table.setItem(row, 1, QTableWidgetItem(exp.date))
            self.table.setItem(row, 2, QTableWidgetItem(exp.category))
            self.table.setItem(row, 3, QTableWidgetItem(str(exp.amount)))
            self.table.setItem(row, 4, QTableWidgetItem(exp.payment_method))
            self.table.setItem(row, 5, QTableWidgetItem(str(exp.rebate)))
