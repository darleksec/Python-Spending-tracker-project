from PyQt6.QtGui import QAction, QKeySequence

def build_menu(window):

    menubar = window.menuBar()

    # Navigation
    nav_menu = menubar.addMenu("Navigate")

    dashboard_action = QAction("Dashboard", window)
    dashboard_action.triggered.connect(window.show_dashboard_page)
    nav_menu.addAction(dashboard_action)

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

    view_menu.addSeparator()

    toggle_sidebar_action = QAction("Toggle Sidebar", window)
    toggle_sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
    toggle_sidebar_action.triggered.connect(window.toggle_sidebar)
    view_menu.addAction(toggle_sidebar_action)

    # Theme
    theme_menu = menubar.addMenu("Theme")

    light_action = QAction("Light Mode", window)
    light_action.triggered.connect(lambda: window.theme_manager.set_theme("light"))
    theme_menu.addAction(light_action)

    dark_action = QAction("Dark Mode", window)
    dark_action.triggered.connect(lambda: window.theme_manager.set_theme("dark"))
    theme_menu.addAction(dark_action)
