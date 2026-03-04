from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QApplication
)
from .entry_page import EntryPage
from .log_page import LogPage
from .visual_page import VisualPage
from .sidebar import Sidebar
from .theme_manager import ThemeManager
from .menu import build_menu

try:
    from .dashboard_page import DashboardPage
except ImportError:
    from PyQt6.QtWidgets import QLabel
    DashboardPage = None


class ExpenseApp(QMainWindow):

    def __init__(self, tracker):
        super().__init__()

        self.setWindowTitle("Expense Tracker")
        self.resize(1200, 700)

        self.tracker = tracker

        # Theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme)

        # Container
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # Sidebar
        self.sidebar = Sidebar(theme_manager=self.theme_manager)
        self.sidebar.set_tracker(self.tracker)
        main_layout.addWidget(self.sidebar, 1)

        # Content Area
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 4)

        # Create pages
        self.enter_page = EntryPage(self.tracker)
        self.log_page = LogPage(self.tracker)
        self.visual_page = VisualPage(self.tracker)

        if DashboardPage is not None:
            self.dashboard_page = DashboardPage(self.tracker)
        else:
            self.dashboard_page = QLabel("Dashboard (coming soon)")

        # Add to stack (indices 0-3)
        self.stack.addWidget(self.enter_page)      # 0
        self.stack.addWidget(self.log_page)         # 1
        self.stack.addWidget(self.visual_page)      # 2
        self.stack.addWidget(self.dashboard_page)   # 3

        # Connect sidebar signals
        self.sidebar.page_requested.connect(self.stack.setCurrentIndex)
        self.sidebar.search_expense_clicked.connect(self._on_search_expense)

        # Build menu
        build_menu(self)

        # Default page
        self.stack.setCurrentWidget(self.enter_page)

        # Apply initial theme
        self.apply_theme(self.theme_manager.get_current_theme())

    def _on_search_expense(self, text):
        """Switch to log page and filter expenses."""
        self.stack.setCurrentIndex(1)
        self.log_page.filter_expenses(text)

    def apply_theme(self, theme_name):
        """Apply the current theme stylesheet to the application."""
        QApplication.instance().setStyleSheet(self.theme_manager.get_stylesheet())

    def show_enter_page(self):
        self.stack.setCurrentWidget(self.enter_page)

    def show_log_page(self):
        self.stack.setCurrentWidget(self.log_page)

    def show_visual_page(self):
        self.stack.setCurrentWidget(self.visual_page)

    def show_dashboard_page(self):
        self.stack.setCurrentIndex(3)

    def toggle_sidebar(self):
        self.sidebar.toggle()
