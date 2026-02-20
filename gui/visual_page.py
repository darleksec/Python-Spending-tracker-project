import sys
import pandas as pd
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox,
    QListWidget, QListWidgetItem,
    QComboBox, QPushButton,
    QTableWidget, QLabel, QFrame, QSizePolicy
)

from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

# class VisualPage(QWidget):

#     def __init__(self, tracker):
#         super().__init__()
#         self.tracker = tracker

#         layout = QVBoxLayout()

#         self.plot_button = QPushButton("Show Category Chart")
#         self.plot_button.clicked.connect(self.plot_data)
        
        
#         self.monthly_pie_label = QLabel("Show monthly breakdown ")
        
#         self.month_dropdown = QComboBox()
        
       
#         months = set()
#         for expense in self.tracker.get_all_expenses():
#             months.add(expense.date[3:10])
            
#         sorted_months = sorted(months)
        
#         self.month_dropdown.addItems(sorted_months)
#         self.month_dropdown.currentTextChanged.connect(self.update_monthly_pie)
        
#         self.MTot_btn = QPushButton("Show Monthly Total Chart")
#         self.MTot_btn.clicked.connect(self.monthly_overview)
        
        
#         self.cat_trend_btn = QPushButton("Show Category Trend Chart")
#         self.cat_trend_btn.clicked.connect(self.plot_category_trend)
        

#         layout.addWidget(self.plot_button)
#         layout.addWidget(self.MTot_btn)
#         layout.addWidget(self.monthly_pie_label)
#         layout.addWidget(self.month_dropdown)
#         layout.addWidget(self.cat_trend_btn)
#         self.setLayout(layout)
        
#     def monthly_overview(self, selected_month):
#         data = []
#         for exp in self.tracker.get_all_expenses():
#             data.append({
#                 "date": exp.date,
#                 "amount":exp.amount
#             })
            
#         df = pd.DataFrame(data)
        
#         df["date"] = pd.to_datetime(df["date"], format = "%d/%m/%Y")
#         df["month"] = df["date"].dt.to_period("M")
        
#         monthly_total = df.groupby("month")["amount"].sum()
#         monthly_total.index = monthly_total.index.astype(str)
        
#         plt.figure()
#         plt.bar(monthly_total.index, monthly_total.values)
#         plt.xlabel("Month")
#         plt.ylabel("Total Spending")
#         plt.title("Monthly Spending Overview")
#         plt.xticks(rotation=45)
#         plt.tight_layout()
#         plt.show()
        
#     def monthly_pie(self, selected_month):
#         data = []
#         for exp in self.tracker.get_all_expenses():
#             data.append({
#                 "date": exp.date,
#                 "amount":exp.amount,
#                 "category": exp.category
#             })
            
#         df = pd.DataFrame(data)
        
#         df["date"] = pd.to_datetime(df["date"], format = "%d/%m/%Y")
        
        
#         df["month"] = df["date"].dt.to_period("M")
        
#         monthly_df = df[df["month"] == selected_month]
        
#         category_totals = monthly_df.groupby("category")["amount"].sum()
        
#         category_totals = category_totals.sort_values(ascending=False)
        
#         top_5 = category_totals.head(5)
        
#         other_total = category_totals.iloc[5:].sum()    
        
#         if other_total > 0:
#             top_5["Other"] = other_total
            
#         fig, ax = plt.subplots()
#         wedges, texts = ax.pie(
#             top_5.values,
#             startangle=90
#         )
        
#         total = top_5.sum()
        
#         for i , wedge in enumerate(wedges):
#             angle = (wedge.theta2 + wedge.theta1) /2
#             x=np.cos(np.deg2rad(angle))
#             y=np.sin(np.deg2rad(angle))
            
#             percentage = top_5.values[i]/ total *100
#             label = f"{top_5.index[i]} ({percentage:.1f}%)"
            
#             ax.annotate(
#                 label,
#                 xy=(x,y),
#                 xytext=(1.1 *x, 1.1 *y),
#                 arrowprops=dict(arrowstyle="-"),
#                 ha="center"
                
#             )
            
#             ax.set_title(f"Spending Breakdown = {selected_month}")
#             plt.tight_layout()
#             plt.show()
            
#     def update_monthly_pie(self):
#         selected_month = self.month_dropdown.currentText()
#         self.monthly_pie(selected_month)
        
#     def create_filters_frame(self):

#         self.filters_group = QGroupBox("Trend Filters")
#         layout = QHBoxLayout()

#         # Category List (Multi-select)
#         self.category_list = QListWidget()
#         self.category_list.setSelectionMode(
#             QListWidget.SelectionMode.MultiSelection
#         )

#         categories = sorted(self.df['Category'].unique())
#         for cat in categories:
#             QListWidgetItem(cat, self.category_list)

#         # Start Month Dropdown
#         self.start_month = QComboBox()

#         # End Month Dropdown
#         self.end_month = QComboBox()

#         self.df['Date'] = pd.to_datetime(self.df['Date'])
#         self.df['Month'] = self.df['Date'].dt.to_period('M')

#         months = sorted(self.df['Month'].astype(str).unique())

#         self.start_month.addItems(months)
#         self.end_month.addItems(months)

#         # Plot Button
#         self.plot_button = QPushButton(" Show Category Trend")
#         self.plot_button.clicked.connect(self.plot_category_trend)

#         # Add widgets to layout
#         layout.addWidget(self.category_list)
#         layout.addWidget(self.start_month)
#         layout.addWidget(self.end_month)
#         layout.addWidget(self.plot_button)

#         self.filters_group.setLayout(layout)
        
#     def create_table_frame(self):

#         self.table_group = QGroupBox("Data / Chart")
#         layout = QVBoxLayout()

#         # Matplotlib Figure
#         self.figure = Figure()
#         self.canvas = FigureCanvas(self.figure)

#         # Optional: Table (placeholder for your log table)
#         self.table = QTableWidget()

#         layout.addWidget(self.canvas)
#         layout.addWidget(self.table)

#         self.table_group.setLayout(layout)
        
#     def plot_category_trend(self):

#         df = self.df.copy()

#         # Selected categories
#         selected_items = self.category_list.selectedItems()
#         selected_categories = [item.text() for item in selected_items]

#         if selected_categories:
#             df = df[df['Category'].isin(selected_categories)]

#         # Month filters
#         start_month = pd.Period(self.start_month.currentText())
#         end_month = pd.Period(self.end_month.currentText())

#         df = df[
#             (df['Month'] >= start_month) &
#             (df['Month'] <= end_month)
#         ]

#         # Group data
#         monthly = (
#             df.groupby(['Month', 'Category'])['Amount']
#               .sum()
#               .reset_index()
#         )

#         if monthly.empty:
#             return

#         pivot_df = monthly.pivot(
#             index='Month',
#             columns='Category',
#             values='Amount'
#         ).fillna(0)

#         # Clear previous plot
#         self.figure.clear()
#         ax = self.figure.add_subplot(111)

#         pivot_df.index = pivot_df.index.astype(str)

#         pivot_df.plot(ax=ax, marker='o')

#         ax.set_title("Category Spending Trend Over Time")
#         ax.set_xlabel("Month")
#         ax.set_ylabel("Total Spending")
#         ax.grid(True)

#         self.canvas.draw()

        
        

        
        
    

        
    


#     def plot_data(self):
#         data = self.tracker.get_category_total()

#         categories = list(data.keys())
#         totals = list(data.values())

#         plt.figure()
#         plt.bar(categories, totals)
#         plt.title("Expenses by Category")
#         plt.xticks(rotation=45)
#         plt.tight_layout()

#         plt.show()



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

        self.apply_modern_style()

        
    def clear_and_get_axis(self):
        self.figure.clear()
        return self.figure.add_subplot(111)
    
        
        
    
    def build_dataframe(self):

        data = []
        for exp in self.tracker.get_all_expenses():
            data.append({
                "Date": exp.date,
                "Category": exp.category,
                "Amount": exp.amount
            })

        df = pd.DataFrame(data)
        print(df.columns)
        print(df.head())


        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
        df["Month"] = df["Date"].dt.to_period("M")

        return df
    
    
    
    
    
    
    def create_filters_frame(self):

        self.filters_group = QGroupBox("Category Trend Filters")
        layout = QHBoxLayout()

        # Category Multi-select
        self.category_list = QListWidget()
        self.category_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection
        )

        categories = sorted(self.df["Category"].unique())
        for cat in categories:
            QListWidgetItem(cat, self.category_list)
            
        self.category_list.selectAll()

        # Start Month
        self.start_month = QComboBox()
        self.end_month = QComboBox()

        months = sorted(self.df["Month"].astype(str).unique())

        self.start_month.addItems(months)
        self.end_month.addItems(months)

        # Trend Button (matches your other buttons style)
        self.cat_trend_btn = QPushButton("Show Category Trend Chart")
        self.cat_trend_btn.clicked.connect(self.plot_category_trend)

        layout.addWidget(self.category_list)
        layout.addWidget(self.start_month)
        layout.addWidget(self.end_month)
        layout.addWidget(self.cat_trend_btn)

        self.filters_group.setLayout(layout)
        
        
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
        
        
        
    def plot_category_trend(self):

        df = self.df.copy()

        # Selected categories
        selected_items = self.category_list.selectedItems()
        selected_categories = [item.text() for item in selected_items]

        if selected_categories:
            df = df[df["Category"].isin(selected_categories)]

        # Month filter
        start_month = pd.Period(self.start_month.currentText())
        end_month = pd.Period(self.end_month.currentText())

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
            index="Month",
            columns="Category",
            values="Amount"
        ).fillna(0)

        pivot_df.index = pivot_df.index.astype(str)

        ax = self.clear_and_get_axis()

        pivot_df.plot(ax=ax, marker="o")

        ax.set_title("Category Spending Trend Over Time")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Spending")
        ax.grid(True)

        # 🔥 LEGEND ON LEFT
        ax.legend(
            title="Category",
            loc="center left",
            bbox_to_anchor=(-0.25, 0.5)
        )

        self.figure.tight_layout()
        self.canvas.draw()


    def plot_cum_spend(self):
        df = self.df.copy()
        
        selected_month = self.start_month.currentText()
        selected_period = pd.Period(selected_month)
        
        current_df = df[df["Month"] == selected_period]
        
        previous_period = selected_period - 1
        previous_df = df[df["Month"] == previous_period]
        
        current_df["Day"] = current_df["Date"].dt.day
        previous_df["Day"] = previous_df["Date"].dt.day
        
        current_daily = current_df.groupby("Day")["Amount"].sum()
        
        previous_daily = previous_df.groupby("Day")["Amount"].sum()
        
        days = range(1,32)
        
        current_daily = current_daily.reindex(days, fill_value=0)
        previous_daily = previous_daily.reindex(days, fill_value=0)
        
        
        current_cumulative = current_daily.cumsum()
        previous_cumulative = previous_daily.cumsum()
        
        ax = self.clear_and_get_axis()
        ax.plot(days, current_cumulative, label=f"{selected_month}")
        ax.plot(days, previous_cumulative, linestyle ="--" ,label=f"{previous_period}")
        
        ax.set_title("Cumulative Spend Comparison")
        ax.set_xlabel("Day of Month")
        ax.set_ylabel("Cumulative Spend (£)")
        ax.grid(True)
        ax.legend(
            loc="center left",
            bbox_to_anchor=(-0.25, 0.5)
        )

        self.figure.tight_layout()
        self.canvas.draw()
        
    def create_sidebar(self):

        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # === QUICK CHARTS SECTION ===
        quick_label = QLabel("Quick Charts")
        quick_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.cat_bar_btn = QPushButton("Category Bar Chart")
        self.cat_bar_btn.clicked.connect(self.Category_Sum)

        self.month_overview_btn = QPushButton("Monthly Overview")
        self.month_overview_btn.clicked.connect(self.monthly_overview)

        self.month_pie_btn = QPushButton("Monthly Pie")
        self.month_pie_btn.clicked.connect(
            lambda: self.monthly_pie(self.start_month.currentText())
        )
        
        self.cumulative_btn = QPushButton("Cumulative Monthly Spend")
        self.cumulative_btn.clicked.connect(self.plot_cum_spend)

        self.cat_trend_btn = QPushButton("Category Trend")
        self.cat_trend_btn.clicked.connect(self.plot_category_trend)

        # === TREND FILTERS SECTION ===
        filter_label = QLabel("Trend Filters")
        filter_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.category_list = QListWidget()
        self.category_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection
        )

        categories = sorted(self.df["Category"].unique())
        for cat in categories:
            QListWidgetItem(cat, self.category_list)

        self.category_list.selectAll()

        self.start_month = QComboBox()
        self.end_month = QComboBox()

        months = sorted(self.df["Month"].astype(str).unique())
        self.start_month.addItems(months)
        self.end_month.addItems(months)

        # Add everything to sidebar layout
        layout.addWidget(quick_label)
        layout.addWidget(self.cat_bar_btn)
        layout.addWidget(self.month_overview_btn)
        layout.addWidget(self.month_pie_btn)
        layout.addWidget(self.cumulative_btn)
        layout.addWidget(self.cat_trend_btn)

        layout.addSpacing(20)

        layout.addWidget(filter_label)
        layout.addWidget(QLabel("Categories"))
        layout.addWidget(self.category_list)
        layout.addWidget(QLabel("Start Month"))
        layout.addWidget(self.start_month)
        layout.addWidget(QLabel("End Month( for Category Trend)"))
        layout.addWidget(self.end_month)

        layout.addStretch()

        self.sidebar_frame.setLayout(layout)

    def create_visual_area(self):

        self.visual_frame = QFrame()
        layout = QVBoxLayout()

        self.chart_title = QLabel("Select a Chart")
        self.chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin: 10px;"
        )

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        layout.addWidget(self.chart_title)
        layout.addWidget(self.canvas)

        self.visual_frame.setLayout(layout)

    def apply_modern_style(self):

        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI;
                font-size: 12px;
            }

            QPushButton {
                padding: 6px;
                border-radius: 6px;
                background-color: #4a90e2;
                color: white;
            }

            QPushButton:hover {
                background-color: #357ABD;
            }

            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
            }

            QFrame {
                background-color: #000000;
            }
        """)
