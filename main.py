import sys
from PyQt6.QtWidgets import QApplication
from gui.app import ExpenseApp
from ExpenseTracker import ExpenseTracker

if __name__ == "__main__":
    app = QApplication(sys.argv)

    tracker = ExpenseTracker()   # Backend instance
    window = ExpenseApp(tracker) # Inject backend

    window.show()
    sys.exit(app.exec())
