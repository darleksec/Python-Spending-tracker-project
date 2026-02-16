from PyQt6.QtGui import QAction

def build_menu(window):

    menubar = window.menuBar()

    # Navigation
    nav_menu = menubar.addMenu("Navigate")

    enter_action = QAction("Enter Expense", window)
    enter_action.triggered.connect(window.show_enter_page)
    nav_menu.addAction(enter_action)

    log_action = QAction("View Log", window)
    log_action.triggered.connect(window.show_log_page)
    nav_menu.addAction(log_action)

    visual_action = QAction("Visualisation", window)
    visual_action.triggered.connect(window.show_visual_page)
    nav_menu.addAction(visual_action)

    # Accessibility
    view_menu = menubar.addMenu("View")

    zoom_in = QAction("Zoom In", window)
    zoom_out = QAction("Zoom Out", window)

    view_menu.addAction(zoom_in)
    view_menu.addAction(zoom_out)
