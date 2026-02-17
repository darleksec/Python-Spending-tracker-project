from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QDateEdit, QFormLayout
)
from PyQt6.QtCore import QDate

class EntryPage(QWidget):
    
    # def __init__(self, tracker):
        #     super().__init__()
        #     self.tracker = tracker

        #     layout = QVBoxLayout()

            
        #     self.date_input = QDateEdit()
        #     self.date_input.setDate(QDate.currentDate())
        #     layout.addWidget(self.date_input)

        #     self.category_input = QLineEdit()
        #     self.category_input.setPlaceholderText("Category")
        #     layout.addWidget(self.category_input)

        #     self.amount_input = QLineEdit()
        #     self.amount_input.setPlaceholderText("Amount")
        #     layout.addWidget(self.amount_input)

        #     self.payment_input = QLineEdit()
        #     self.payment_input.setPlaceholderText("Payment Method")  
        #     layout.addWidget(self.payment_input)

        #     self.rebate_input = QLineEdit()
        #     layout.addWidget(QLabel("Rebate"))
        #     layout.addWidget(self.rebate_input)

        #     submit = QPushButton("Add Expense")
        #     submit.clicked.connect(self.add_expense)

        #     layout.addWidget(submit)
        #     self.setLayout(layout)

        # def add_expense(self):
        #     self.tracker.add_expense(
        #         date=self.date_input.date().toString("yyyy-MM-dd"),
        #         category=self.category_input.text(),
        #         amount=float(self.amount_input.text()),
        #         payment_method=self.payment_input.text(),
        #         rebate=float(self.rebate_input.text() or 0)
        #     )
            
        #     self.category_input.clear()
        #     self.amount_input.clear()
        #     self.payment_input.clear()
        #     self.rebate_input.clear()

    def __init__(self, tracker):
            super().__init__()
            self.tracker = tracker

            layout = QVBoxLayout()
            form = QFormLayout()


            
            self.date_input = QDateEdit()
            self.date_input.setDate(QDate.currentDate())

            self.category_input = QLineEdit()
            self.amount_input = QLineEdit()
            self.payment_input = QLineEdit()
            self.merchant_input = QLineEdit()
            self.rebate_input = QLineEdit()

            form.addRow("Date:", self.date_input)
            form.addRow("Category:", self.category_input)
            form.addRow("Amount:", self.amount_input)
            form.addRow("Payment:", self.payment_input)
            form.addRow("Merchant:", self.merchant_input)
            form.addRow("Rebate:", self.rebate_input)

            layout.addLayout(form)

            submit = QPushButton("Add Expense")
            submit.clicked.connect(self.add_expense)

            layout.addWidget(submit)
            self.setLayout(layout)

    def add_expense(self):
        self.tracker.add_expense(
            date=self.date_input.date().toString("yyyy-MM-dd"),
            category=self.category_input.text(),
            amount=float(self.amount_input.text()),
            payment_method=self.payment_input.text(),
            merchant=self.merchant_input.text(),
            rebate=float(self.rebate_input.text() or 0)
        )
        
        self.category_input.clear()
        self.amount_input.clear()
        self.payment_input.clear()
        self.merchant_input.clear()
        self.rebate_input.clear()

