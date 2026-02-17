import sys
# import os
from PyQt6.QtWidgets import QApplication
from gui.app import ExpenseApp
from ExpenseTracker import ExpenseTracker



if __name__ == "__main__":
    app = QApplication(sys.argv)

    tracker = ExpenseTracker()   # Backend instance
    window = ExpenseApp(tracker) # Inject backend
    
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())


    window.show()
    sys.exit(app.exec())
