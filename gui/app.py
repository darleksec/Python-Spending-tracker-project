from PyQt6.QtWidgets import (  QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget)
from PyQt6.QtCore import Qt
from .entry_page import EntryPage
from .log_page import LogPage
from .visual_page import VisualPage
from .menu import build_menu


class ExpenseApp(QMainWindow):

    def __init__(self, tracker):
        super().__init__()

        self.setWindowTitle("Expense Tracker")
        self.resize(1200, 700)

        self.tracker = tracker
        
        #Container
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)
        
        #Sidebar
        
        self.sidebar = QVBoxLayout()
        main_layout.addLayout(self.sidebar, 1)
        
        #Content Area
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 4)
        
        

       

        # Create pages
        self.enter_page = EntryPage(self.tracker)
        self.log_page = LogPage(self.tracker)
        self.visual_page = VisualPage(self.tracker)

        # Add to stack
        self.stack.addWidget(self.enter_page)
        self.stack.addWidget(self.log_page)
        self.stack.addWidget(self.visual_page)
        
        self.add_sidebar_btn("Add Expenses", 0)
        self.add_sidebar_btn("Expense Log", 1)
        self.add_sidebar_btn("Analytics ", 2)
        

        # Build menu
        build_menu(self)

        # Default page
        self.stack.setCurrentWidget(self.enter_page)

    def show_enter_page(self):
        self.stack.setCurrentWidget(self.enter_page)

    def show_log_page(self):
        self.stack.setCurrentWidget(self.log_page)

    def show_visual_page(self):
        self.stack.setCurrentWidget(self.visual_page)
        
    def add_sidebar_btn(self, text, index):
        btn = QPushButton(text)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar.addWidget(btn)
        
        
    
