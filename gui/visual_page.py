import sys
import pandas as pd
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox,
    QListWidget, QListWidgetItem,
    QComboBox, QPushButton,
    QTableWidget, QLabel, QFrame, QSizePolicy,
    QDialog, QDialogButtonBox
)

from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class FilterDialog(QDialog):
    """Popup dialog for selecting categories and month range for trend charts."""

    def __init__(self, categories, months, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chart Filters")
        self.setMinimumWidth(350)
        self.setMinimumHeight(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Select Categories:"))
        self.category_list = QListWidget()
        self.category_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection
        )
        for cat in categories:
            QListWidgetItem(cat, self.category_list)
        self.category_list.selectAll()
        layout.addWidget(self.category_list)

        layout.addWidget(QLabel("Start Month:"))
        self.start_month = QComboBox()
        self.start_month.addItems(months)
        layout.addWidget(self.start_month)

        layout.addWidget(QLabel("End Month:"))
        self.end_month = QComboBox()
        self.end_month.addItems(months)
        if months:
            self.end_month.setCurrentIndex(len(months) - 1)
        layout.addWidget(self.end_month)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_categories(self):
        return [item.text() for item in self.category_list.selectedItems()]

    def get_start_month(self):
        return self.start_month.currentText()

    def get_end_month(self):
        return self.end_month.currentText()


class VisualPage(QWidget):

    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker

        self.df = self.build_dataframe()

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # LEFT SIDEBAR
        self.create_sidebar()

        # RIGHT VISUAL AREA
        self.create_visual_area()

        main_layout.addWidget(self.sidebar_frame, 1)
        main_layout.addWidget(self.visual_frame, 3)


    def clear_and_get_axis(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor('none')
        ax.set_facecolor('none')
        return ax


    def build_dataframe(self):

        expenses = self.tracker.get_all_expenses()
        if not expenses:
            return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Month'])

        data = []
        for exp in expenses:
            data.append({
                "Date": exp.date,
                "Category": exp.category,
                "Amount": exp.amount
            })

        df = pd.DataFrame(data)

        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
        df["Month"] = df["Date"].dt.to_period("M")

        return df


    def create_chart_frame(self):

        self.chart_group = QGroupBox("Chart Output")
        layout = QVBoxLayout()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)
        self.chart_group.setLayout(layout)




    def Category_Sum(self):

        data = self.tracker.get_category_total()

        categories = list(data.keys())
        totals = list(data.values())

        ax = self.clear_and_get_axis()

        ax.bar(categories, totals)
        ax.set_title("Expenses by Category")
        ax.set_xlabel("Category")
        ax.set_ylabel("Total Spending")
        ax.tick_params(axis='x', rotation=45)

        self.canvas.draw()


    def monthly_overview(self):

        df = self.df.copy()

        monthly_total = df.groupby("Month")["Amount"].sum()
        monthly_total.index = monthly_total.index.astype(str)

        ax = self.clear_and_get_axis()

        ax.bar(monthly_total.index, monthly_total.values)

        ax.set_title("Monthly Spending Overview")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Spending")
        ax.tick_params(axis='x', rotation=45)

        self.canvas.draw()

    def monthly_pie(self, selected_month):

        df = self.df.copy()

        monthly_df = df[df["Month"].astype(str) == selected_month]

        category_totals = monthly_df.groupby("Category")["Amount"].sum()
        category_totals = category_totals.sort_values(ascending=False)

        top_5 = category_totals.head(5)
        other_total = category_totals.iloc[5:].sum()

        if other_total > 0:
            top_5["Other"] = other_total

        ax = self.clear_and_get_axis()

        wedges, texts = ax.pie(
            top_5.values,
            startangle=90
        )

        total = top_5.sum()

        for i, wedge in enumerate(wedges):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = np.cos(np.deg2rad(angle))
            y = np.sin(np.deg2rad(angle))

            percentage = top_5.values[i] / total * 100
            label = f"{top_5.index[i]} ({percentage:.1f}%)"

            ax.annotate(
                label,
                xy=(x, y),
                xytext=(1.2 * x, 1.2 * y),
                arrowprops=dict(arrowstyle="-"),
                ha="center"
            )

        ax.set_title(f"Spending Breakdown — {selected_month}")

        self.canvas.draw()



    def _plot_cum_spend_for_month(self, month):
        """Wrapper: plot cumulative spend for a selected month (from dialog)."""
        df = self.df.copy()
        selected_period = pd.Period(month)
        previous_period = selected_period - 1

        current_df = df[df["Month"] == selected_period]
        previous_df = df[df["Month"] == previous_period]

        current_df = current_df.copy()
        previous_df = previous_df.copy()

        current_df["Day"] = current_df["Date"].dt.day
        previous_df["Day"] = previous_df["Date"].dt.day

        current_daily = current_df.groupby("Day")["Amount"].sum()
        previous_daily = previous_df.groupby("Day")["Amount"].sum()

        days = range(1, 32)
        current_daily = current_daily.reindex(days, fill_value=0)
        previous_daily = previous_daily.reindex(days, fill_value=0)

        ax = self.clear_and_get_axis()
        ax.plot(days, current_daily.cumsum(), label=f"{month}")
        ax.plot(days, previous_daily.cumsum(), linestyle="--", label=f"{previous_period}")

        ax.set_title("Cumulative Spend Comparison")
        ax.set_xlabel("Day of Month")
        ax.set_ylabel("Cumulative Spend (£)")
        ax.grid(True)
        ax.legend(loc="center left", bbox_to_anchor=(-0.25, 0.5))

        self.figure.tight_layout()
        self.canvas.draw()

    def _plot_category_trend_filtered(self):
        """Plot category trend using selections from the filter dialog."""
        df = self.df.copy()

        selected_categories = self._last_categories
        if selected_categories:
            df = df[df["Category"].isin(selected_categories)]

        start_month = pd.Period(self._last_start_month)
        end_month = pd.Period(self._last_end_month)

        df = df[
            (df["Month"] >= start_month) &
            (df["Month"] <= end_month)
        ]

        monthly = (
            df.groupby(["Month", "Category"])["Amount"]
            .sum()
            .reset_index()
        )

        if monthly.empty:
            return

        pivot_df = monthly.pivot(
            index="Month", columns="Category", values="Amount"
        ).fillna(0)
        pivot_df.index = pivot_df.index.astype(str)

        ax = self.clear_and_get_axis()
        pivot_df.plot(ax=ax, marker="o")

        ax.set_title("Category Spending Trend Over Time")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Spending")
        ax.grid(True)
        ax.legend(title="Category", loc="center left", bbox_to_anchor=(-0.25, 0.5))

        self.figure.tight_layout()
        self.canvas.draw()

    def _get_categories_and_months(self):
        """Return sorted categories and months from current data."""
        categories = sorted(self.df["Category"].unique()) if not self.df.empty else []
        months = sorted(self.df["Month"].astype(str).unique()) if not self.df.empty else []
        return categories, months

    def _open_filter_and_run(self, chart_func):
        """Open filter dialog, then run the chart function with selected filters."""
        categories, months = self._get_categories_and_months()
        if not categories and not months:
            return

        dlg = FilterDialog(categories, months, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._last_categories = dlg.get_selected_categories()
            self._last_start_month = dlg.get_start_month()
            self._last_end_month = dlg.get_end_month()
            chart_func()

    def _open_month_picker_and_run(self, chart_func):
        """Open a simple month picker dialog for charts that just need a month."""
        _, months = self._get_categories_and_months()
        if not months:
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Select Month")
        dlg.setMinimumWidth(250)
        lay = QVBoxLayout()
        dlg.setLayout(lay)
        lay.addWidget(QLabel("Month:"))
        combo = QComboBox()
        combo.addItems(months)
        combo.setCurrentIndex(len(months) - 1)
        lay.addWidget(combo)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        lay.addWidget(buttons)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            chart_func(combo.currentText())

    def create_sidebar(self):

        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName('visualSidebar')
        self.sidebar_frame.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Store last filter selections for trend charts
        self._last_categories = []
        self._last_start_month = ""
        self._last_end_month = ""

        # === CHARTS SECTION ===
        quick_label = QLabel("Charts")

        self.cat_bar_btn = QPushButton("Category Bar Chart")
        self.cat_bar_btn.clicked.connect(self.Category_Sum)

        self.month_overview_btn = QPushButton("Monthly Overview")
        self.month_overview_btn.clicked.connect(self.monthly_overview)

        self.month_pie_btn = QPushButton("Monthly Pie...")
        self.month_pie_btn.clicked.connect(
            lambda: self._open_month_picker_and_run(self.monthly_pie)
        )

        self.cumulative_btn = QPushButton("Cumulative Spend...")
        self.cumulative_btn.clicked.connect(
            lambda: self._open_month_picker_and_run(self._plot_cum_spend_for_month)
        )

        self.cat_trend_btn = QPushButton("Category Trend...")
        self.cat_trend_btn.clicked.connect(
            lambda: self._open_filter_and_run(self._plot_category_trend_filtered)
        )

        layout.addWidget(quick_label)
        layout.addWidget(self.cat_bar_btn)
        layout.addWidget(self.month_overview_btn)
        layout.addWidget(self.month_pie_btn)
        layout.addWidget(self.cumulative_btn)
        layout.addWidget(self.cat_trend_btn)

        layout.addStretch()

        self.sidebar_frame.setLayout(layout)

    def create_visual_area(self):

        self.visual_frame = QFrame()
        self.visual_frame.setObjectName('visualContent')
        layout = QVBoxLayout()

        self.chart_title = QLabel("Select a Chart")
        self.chart_title.setObjectName('chartTitle')
        self.chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.figure = Figure()
        self.figure.patch.set_facecolor('none')
        self.canvas = FigureCanvas(self.figure)

        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        layout.addWidget(self.chart_title)
        layout.addWidget(self.canvas)

        self.visual_frame.setLayout(layout)
