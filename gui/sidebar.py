from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QListWidget, QListWidgetItem,
    QLabel, QSizePolicy, QWidget, QSpacerItem
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
)


class Sidebar(QFrame):
    """Collapsible sidebar with navigation, search, and theme switching."""

    EXPANDED_WIDTH = 250
    COLLAPSED_WIDTH = 50
    ANIMATION_DURATION = 300

    page_requested = pyqtSignal(int)
    search_expense_clicked = pyqtSignal(str)
    sidebar_toggled = pyqtSignal(bool)

    NAV_ITEMS = [
        ("Add Expenses", 0),
        ("Expense Log", 1),
        ("Analytics", 2),
        ("Dashboard", 3),
    ]

    def __init__(self, theme_manager=None, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._expanded = True
        self._animating = False
        self._theme_manager = theme_manager
        self._tracker = None

        self.setMinimumWidth(self.COLLAPSED_WIDTH)
        self.setMaximumWidth(self.EXPANDED_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self._setup_animation()
        self._build_ui()

    def _setup_animation(self):
        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(self.ANIMATION_DURATION)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._anim.finished.connect(self._on_animation_finished)

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setLayout(layout)

        # Toggle button row
        toggle_row = QHBoxLayout()
        toggle_row.addStretch()
        self._toggle_btn = QPushButton("<<")
        self._toggle_btn.setObjectName("sidebar_toggle")
        self._toggle_btn.setFixedSize(36, 36)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.clicked.connect(self.toggle)
        toggle_row.addWidget(self._toggle_btn)
        layout.addLayout(toggle_row)

        # Search bar
        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("Search...")
        self._search_bar.setObjectName("sidebar_search")
        self._search_bar.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_bar)

        # Navigation buttons
        self._nav_buttons = []
        for text, index in self.NAV_ITEMS:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("sidebar_nav_btn")
            btn.clicked.connect(lambda checked=False, i=index: self.page_requested.emit(i))
            layout.addWidget(btn)
            self._nav_buttons.append((text, btn))

        # Search results list
        self._results_list = QListWidget()
        self._results_list.setObjectName("sidebar_results")
        self._results_list.setMaximumHeight(200)
        self._results_list.itemClicked.connect(
            lambda item: self.search_expense_clicked.emit(item.text())
        )
        self._results_list.hide()
        layout.addWidget(self._results_list)

        # No results label
        self._no_results_label = QLabel("No results")
        self._no_results_label.setObjectName("sidebar_no_results")
        self._no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_results_label.hide()
        layout.addWidget(self._no_results_label)

        # Spacer
        layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        # Theme dropdown
        self._theme_combo = QComboBox()
        self._theme_combo.setObjectName("sidebar_theme")
        self._theme_combo.addItems(["Light", "Dark"])
        if self._theme_manager:
            current = self._theme_manager.get_current_theme()
            self._theme_combo.setCurrentText(current.capitalize())
        self._theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addWidget(self._theme_combo)

    def set_tracker(self, tracker):
        """Set the expense tracker for search functionality."""
        self._tracker = tracker

    def toggle(self):
        """Toggle sidebar expand/collapse with animation."""
        if self._animating:
            return

        self._animating = True
        if self._expanded:
            self._anim.setStartValue(self.EXPANDED_WIDTH)
            self._anim.setEndValue(self.COLLAPSED_WIDTH)
        else:
            self._anim.setStartValue(self.COLLAPSED_WIDTH)
            self._anim.setEndValue(self.EXPANDED_WIDTH)

        self._anim.start()

    def _on_animation_finished(self):
        self._expanded = not self._expanded
        self._animating = False
        self._toggle_btn.setText(">>" if not self._expanded else "<<")
        self._update_collapsed_state()
        self.sidebar_toggled.emit(self._expanded)

    def _update_collapsed_state(self):
        """Show/hide widgets based on collapsed state."""
        visible = self._expanded
        self._search_bar.setVisible(visible)
        for _, btn in self._nav_buttons:
            btn.setVisible(visible)
        self._theme_combo.setVisible(visible)
        self._results_list.setVisible(visible and self._results_list.count() > 0)
        self._no_results_label.setVisible(False)

    def _on_search_changed(self, text):
        """Filter nav buttons and search expenses by text."""
        text_lower = text.strip().lower()

        # Filter nav buttons
        if not text_lower:
            for _, btn in self._nav_buttons:
                btn.show()
            self._results_list.hide()
            self._no_results_label.hide()
            return

        any_nav_visible = False
        for label, btn in self._nav_buttons:
            match = text_lower in label.lower()
            btn.setVisible(match)
            if match:
                any_nav_visible = True

        # Search expenses
        self._results_list.clear()
        matches = []
        if self._tracker:
            try:
                expenses = self._tracker.get_all_expenses()
                for exp in expenses:
                    cat = getattr(exp, "category", "") or ""
                    merchant = getattr(exp, "merchant", "") or ""
                    if text_lower in cat.lower() or text_lower in merchant.lower():
                        entry = f"{cat} - {merchant}"
                        if entry not in matches:
                            matches.append(entry)
                        if len(matches) >= 10:
                            break
            except Exception:
                pass

        if matches:
            for m in matches:
                item = QListWidgetItem(m)
                fm = item.font()
                self._results_list.addItem(item)
            self._results_list.show()
            self._no_results_label.hide()
        else:
            self._results_list.hide()
            if not any_nav_visible:
                self._no_results_label.show()
            else:
                self._no_results_label.hide()

    def _on_theme_changed(self, text):
        """Handle theme dropdown change."""
        if self._theme_manager:
            self._theme_manager.set_theme(text.lower())

    def is_expanded(self):
        """Return whether the sidebar is currently expanded."""
        return self._expanded
