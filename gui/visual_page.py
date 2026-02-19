from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QLabel
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class VisualPage(QWidget):

    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker

        layout = QVBoxLayout()

        self.plot_button = QPushButton("Show Category Chart")
        self.plot_button.clicked.connect(self.plot_data)
        
        
        self.monthly_pie_label = QLabel("Show monthly breakdown ")
        
        self.month_dropdown = QComboBox()
        
       
        months = set()
        for expense in self.tracker.get_all_expenses():
            months.add(expense.date[3:10])
            
        sorted_months = sorted(months)
        
        self.month_dropdown.addItems(sorted_months)
        self.month_dropdown.currentTextChanged.connect(self.update_monthly_pie)
        
        self.MTot_btn = QPushButton("Show Monthly Total Chart")
        self.MTot_btn.clicked.connect(self.monthly_overview)

        

        layout.addWidget(self.plot_button)
        layout.addWidget(self.MTot_btn)
        layout.addWidget(self.monthly_pie_label)
        layout.addWidget(self.month_dropdown)
        self.setLayout(layout)
        
    def monthly_overview(self, selected_month):
        data = []
        for exp in self.tracker.get_all_expenses():
            data.append({
                "date": exp.date,
                "amount":exp.amount
            })
            
        df = pd.DataFrame(data)
        
        df["date"] = pd.to_datetime(df["date"], format = "%d/%m/%Y")
        df["month"] = df["date"].dt.to_period("M")
        
        monthly_total = df.groupby("month")["amount"].sum()
        monthly_total.index = monthly_total.index.astype(str)
        
        plt.figure()
        plt.bar(monthly_total.index, monthly_total.values)
        plt.xlabel("Month")
        plt.ylabel("Total Spending")
        plt.title("Monthly Spending Overview")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    def monthly_pie(self, selected_month):
        data = []
        for exp in self.tracker.get_all_expenses():
            data.append({
                "date": exp.date,
                "amount":exp.amount,
                "category": exp.category
            })
            
        df = pd.DataFrame(data)
        
        df["date"] = pd.to_datetime(df["date"], format = "%d/%m/%Y")
        
        
        df["month"] = df["date"].dt.to_period("M")
        
        monthly_df = df[df["month"] == selected_month]
        
        category_totals = monthly_df.groupby("category")["amount"].sum()
        
        category_totals = category_totals.sort_values(ascending=False)
        
        top_5 = category_totals.head(5)
        
        other_total = category_totals.iloc[5:].sum()    
        
        if other_total > 0:
            top_5["Other"] = other_total
            
        fig, ax = plt.subplots()
        wedges, texts = ax.pie(
            top_5.values,
            startangle=90
        )
        
        total = top_5.sum()
        
        for i , wedge in enumerate(wedges):
            angle = (wedge.theta2 + wedge.theta1) /2
            x=np.cos(np.deg2rad(angle))
            y=np.sin(np.deg2rad(angle))
            
            percentage = top_5.values[i]/ total *100
            label = f"{top_5.index[i]} ({percentage:.1f}%)"
            
            ax.annotate(
                label,
                xy=(x,y),
                xytext=(1.1 *x, 1.1 *y),
                arrowprops=dict(arrowstyle="-"),
                ha="center"
                
            )
            
            ax.set_title(f"Spending Breakdown = {selected_month}")
            plt.tight_layout()
            plt.show()
            
    def update_monthly_pie(self):
        selected_month = self.month_dropdown.currentText()
        self.monthly_pie(selected_month)
        


    def plot_data(self):
        data = self.tracker.get_category_total()

        categories = list(data.keys())
        totals = list(data.values())

        plt.figure()
        plt.bar(categories, totals)
        plt.title("Expenses by Category")
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.show()
