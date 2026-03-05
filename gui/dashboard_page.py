import pandas as pd
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QComboBox, QLabel,
)
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class DashboardPage(QWidget):

    def __init__(self, tracker, theme_manager=None):
        super().__init__()
        self.setObjectName("dashboard")
        self.tracker = tracker
        self.theme_manager = theme_manager

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.month_selector = self.create_month_selector()
        layout.addWidget(self.month_selector)

        self.figures = []
        self.canvases = []
        self.grid_widget = self.create_chart_grid()
        layout.addWidget(self.grid_widget)

        # Initial draw
        if self.month_selector.count() > 0:
            self.month_selector.setCurrentIndex(self.month_selector.count() - 1)
            self.update_all_charts(self.month_selector.currentText())

        self.month_selector.currentTextChanged.connect(self.update_all_charts)

    def build_dataframe(self):
        expenses = self.tracker.get_all_expenses()
        if not expenses:
            return pd.DataFrame(columns=["Date", "Category", "Amount", "Merchant"])

        data = []
        for exp in expenses:
            data.append({
                "Date": exp.date,
                "Category": exp.category,
                "Amount": exp.amount,
                "Merchant": getattr(exp, "merchant", "Unknown"),
            })

        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
        df["Month"] = df["Date"].dt.to_period("M")
        return df

    def create_month_selector(self):
        combo = QComboBox()
        df = self.build_dataframe()
        if not df.empty:
            months = sorted(df["Month"].astype(str).unique())
            combo.addItems(months)
        return combo

    def create_chart_grid(self):
        widget = QWidget()
        grid = QGridLayout()
        widget.setLayout(grid)

        self.figures = []
        self.canvases = []

        for row in range(2):
            for col in range(2):
                fig = Figure(tight_layout=True)
                canvas = FigureCanvas(fig)
                self.figures.append(fig)
                self.canvases.append(canvas)
                grid.addWidget(canvas, row, col)

        return widget

    def _get_chart_style(self):
        if self.theme_manager:
            return self.theme_manager.get_chart_colors()
        return {"bg": "#FFFFFF", "text": "#1F2328", "grid": "#D0D7DE", "accent": "#1a67b3"}

    def _style_ax(self, ax, title):
        colors = self._get_chart_style()
        ax.set_facecolor(colors["bg"])
        ax.figure.set_facecolor(colors["bg"])
        ax.set_title(title, color=colors["text"])
        ax.tick_params(colors=colors["text"])
        for spine in ax.spines.values():
            spine.set_edgecolor(colors["grid"])

    def _show_no_data(self, ax, title=""):
        ax.clear()
        self._style_ax(ax, title)
        ax.text(0.5, 0.5, "No data for this month",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=12, color=self._get_chart_style()["text"])

    def update_all_charts(self, month):
        df = self.build_dataframe()

        if df.empty:
            for i, fig in enumerate(self.figures):
                fig.clear()
                ax = fig.add_subplot(111)
                self._show_no_data(ax)
                self.canvases[i].draw()
            return

        monthly_df = df[df["Month"].astype(str) == month]

        self._draw_category_pie(self.figures[0], monthly_df, month)
        self.canvases[0].draw()

        self._draw_daily_bar(self.figures[1], monthly_df, month)
        self.canvases[1].draw()

        self._draw_cumulative_line(self.figures[2], df, month)
        self.canvases[2].draw()

        self._draw_top_merchants(self.figures[3], monthly_df, month)
        self.canvases[3].draw()

    def _draw_category_pie(self, fig, monthly_df, month):
        fig.clear()
        ax = fig.add_subplot(111)

        if monthly_df.empty:
            self._show_no_data(ax, f"Category Breakdown — {month}")
            return

        colors = self._get_chart_style()
        category_totals = monthly_df.groupby("Category")["Amount"].sum()
        category_totals = category_totals.sort_values(ascending=False)

        top_5 = category_totals.head(5).copy()
        other_total = category_totals.iloc[5:].sum()
        if other_total > 0:
            top_5["Other"] = other_total

        wedges, texts, autotexts = ax.pie(
            top_5.values, labels=top_5.index, startangle=90,
            autopct="%1.1f%%", textprops={"color": colors["text"]},
        )
        self._style_ax(ax, f"Category Breakdown — {month}")

    def _draw_daily_bar(self, fig, monthly_df, month):
        fig.clear()
        ax = fig.add_subplot(111)

        if monthly_df.empty:
            self._show_no_data(ax, f"Daily Spending — {month}")
            return

        colors = self._get_chart_style()
        monthly_df = monthly_df.copy()
        monthly_df["Day"] = monthly_df["Date"].dt.day
        daily = monthly_df.groupby("Day")["Amount"].sum()

        ax.bar(daily.index, daily.values, color=colors["accent"])
        ax.set_xlabel("Day of Month", color=colors["text"])
        ax.set_ylabel("Amount", color=colors["text"])
        self._style_ax(ax, f"Daily Spending — {month}")

    def _draw_cumulative_line(self, fig, df, month):
        fig.clear()
        ax = fig.add_subplot(111)
        colors = self._get_chart_style()

        selected_period = pd.Period(month)
        previous_period = selected_period - 1

        current_df = df[df["Month"] == selected_period].copy()
        previous_df = df[df["Month"] == previous_period].copy()

        if current_df.empty and previous_df.empty:
            self._show_no_data(ax, "Cumulative Spend")
            return

        days = range(1, 32)

        if not current_df.empty:
            current_df["Day"] = current_df["Date"].dt.day
            current_daily = current_df.groupby("Day")["Amount"].sum().reindex(days, fill_value=0)
            ax.plot(days, current_daily.cumsum(), label=str(selected_period), color=colors["accent"])

        if not previous_df.empty:
            previous_df["Day"] = previous_df["Date"].dt.day
            previous_daily = previous_df.groupby("Day")["Amount"].sum().reindex(days, fill_value=0)
            ax.plot(days, previous_daily.cumsum(), linestyle="--", label=str(previous_period))

        ax.set_xlabel("Day of Month", color=colors["text"])
        ax.set_ylabel("Cumulative Spend", color=colors["text"])
        ax.legend()
        ax.grid(True, color=colors["grid"], alpha=0.3)
        self._style_ax(ax, "Cumulative Spend Comparison")

    def _draw_top_merchants(self, fig, monthly_df, month):
        fig.clear()
        ax = fig.add_subplot(111)

        if monthly_df.empty:
            self._show_no_data(ax, f"Top Merchants — {month}")
            return

        colors = self._get_chart_style()
        merchant_totals = monthly_df.groupby("Merchant")["Amount"].sum()
        merchant_totals = merchant_totals.sort_values(ascending=True).tail(10)

        ax.barh(merchant_totals.index, merchant_totals.values, color=colors["accent"])
        ax.set_xlabel("Total Spending", color=colors["text"])
        self._style_ax(ax, f"Top Merchants — {month}")
