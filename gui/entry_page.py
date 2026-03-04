from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QDateEdit, QFormLayout, QMessageBox
)
from PyQt6.QtCore import QDate


class EntryPage(QWidget):

    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("Add New Expense")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(10)

        self.create_form_fields()

        form.addRow("Date:", self.date_input)
        form.addRow("Category:", self.category_input)
        form.addRow("Amount:", self.amount_input)
        form.addRow("Payment:", self.payment_input)
        form.addRow("Merchant:", self.merchant_input)
        form.addRow("Rebate:", self.rebate_input)

        layout.addLayout(form)

        self.create_submit_section()
        layout.addWidget(self.submit_btn)

        self.setup_signals()
        self.setLayout(layout)

    def create_form_fields(self):
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g. Food, Transport...")

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("e.g. 25.50")

        self.payment_input = QLineEdit()
        self.payment_input.setPlaceholderText("e.g. Card, Cash...")

        self.merchant_input = QLineEdit()
        self.merchant_input.setPlaceholderText("e.g. Tesco, Amazon...")

        self.rebate_input = QLineEdit()
        self.rebate_input.setPlaceholderText("0.00 (optional)")

    def create_submit_section(self):
        self.submit_btn = QPushButton("Add Expense")
        self.submit_btn.setObjectName("submitButton")
        self.submit_btn.clicked.connect(self.submit_add_expense)

    def setup_signals(self):
        self.amount_input.textChanged.connect(self.check_form_complete)
        self.category_input.textChanged.connect(self.check_form_complete)
        self.payment_input.textChanged.connect(self.check_form_complete)
        self.merchant_input.textChanged.connect(self.check_form_complete)
        self.rebate_input.textChanged.connect(self.check_form_complete)

    def add_expense(self):
        self.tracker.add_expense(
            date=self.date_input.date().toString("dd/MM/yyyy"),
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

    def submit_add_expense(self):
        self.check_form_complete()
        if not self.validate_inputs():
            return
        self.add_expense()
        QMessageBox.information(self, " Success", "Expense saved")

    def validate_inputs(self):

        if not self.amount_input.text().strip():
            QMessageBox.warning(self, "Missing Field", "Amount is required.")
            return False

        if not self.category_input.text().strip():
            QMessageBox.warning(self, "Missing Field", "Category is required.")
            return False

        if not self.payment_input.text().strip():
            QMessageBox.warning(self, "Missing Field", "Payment Method is required.")
            return False

        if not self.merchant_input.text().strip():
            QMessageBox.warning(self, "Missing Field", "Merchant is required.")
            return False

        return True

    def check_form_complete(self):

        if (
            self.amount_input.text().strip()
            and self.category_input.text().strip()
            and self.payment_input.text().strip()
            and self.merchant_input.text().strip()
        ):
            self.submit_btn.setEnabled(True)
        else:
            self.submit_btn.setEnabled(False)
