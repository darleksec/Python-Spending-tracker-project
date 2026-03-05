import sys
from PyQt6.QtWidgets import QApplication
from gui.app import ExpenseApp
from ExpenseTracker import ExpenseTracker



if __name__ == "__main__":
    app = QApplication(sys.argv)

    tracker = ExpenseTracker()   # Backend instance
    window = ExpenseApp(tracker) # Inject backend

    # Apply initial theme via ThemeManager (style.qss kept on disk as fallback only)
    app.setStyleSheet(window.theme_manager.get_stylesheet())

    window.show()
    sys.exit(app.exec())
