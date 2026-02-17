from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QFileDialog, QAbstractItemView, QMessageBox, 
)
from PyQt6.QtCore import Qt

class LogPage(QWidget):

    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker
        
        layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by category...")
        layout.addWidget(self.search_input)
        submit = QPushButton("Import CSV")
        submit.clicked.connect(self.import_spreadsheet)
        layout.addWidget(submit)


        #table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Date", "Category", "Amount", "Payment","Merchant", "Rebate"]
        )
        self.table.setSortingEnabled(True)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.itemChanged.connect(self.handle_item_changed)

        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row)
            
        selected_rows = list(selected_rows)
            

        layout.addWidget(self.table)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        layout.addWidget(self.delete_button)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        self.load_data()








    def load_data(self):
        expenses = self.tracker.get_all_expenses()
        
        self.table.blockSignals(True)  # prevent itemChanged firing
        
        self.table.setRowCount(len(expenses))

        for row, exp in enumerate(expenses):
            # ID (non-editable)
            id_item = QTableWidgetItem(str(exp.id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, id_item)

            self.table.setItem(row, 1, QTableWidgetItem(exp.date))
            self.table.setItem(row, 2, QTableWidgetItem(exp.category))
            self.table.setItem(row, 3, QTableWidgetItem(str(exp.amount)))
            self.table.setItem(row, 4, QTableWidgetItem(exp.payment_method))
            self.table.setItem(row, 5, QTableWidgetItem(exp.merchant))
            self.table.setItem(row, 6, QTableWidgetItem(str(exp.rebate)))

        self.table.setColumnHidden(0, True)

        self.table.blockSignals(False)



    def import_spreadsheet(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            count = self.tracker.importCSV(file_path)
            print(f"{count} expenses imported")
            self.load_data()
        
        
        
    def get_expense_id_from_row(self, row):
        item = self.table.item(row, 0)  # Column 0 = ID
        return int(item.text())
    
    


    
        
    def delete_selected(self):
        selected_indexes = self.table.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.warning(self, "Delete Error",
                                "Please select at least one expense.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(selected_indexes)} selected expense(s)?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        for index in selected_indexes:
            row = index.row()
            expense_id = self.get_expense_id_from_row(row)
            self.tracker.delete_expense(expense_id)

        self.load_data()




    def handle_item_changed(self, item):
        row = item.row()
        column = item.column()

        if column == 0:
            return  # ID should not be edited

        expense_id = int(self.table.item(row, 0).text())
        new_value = item.text()

        expense = self.tracker.get_expense_by_id(expense_id)

        if not expense:
            return

        try:
            if column == 1:
                expense.date = new_value

            elif column == 2:
                expense.category = new_value

            elif column == 3:
                expense.amount = float(new_value)

            elif column == 4:
                expense.payment_method = new_value

            elif column == 5:
                expense.merchant = new_value

            elif column == 6:
                expense.rebate = float(new_value)

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Invalid value entered.")
            self.load_data()
