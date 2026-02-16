from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
import matplotlib.pyplot as plt

class VisualPage(QWidget):

    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker

        layout = QVBoxLayout()

        self.plot_button = QPushButton("Show Category Chart")
        self.plot_button.clicked.connect(self.plot_data)

        layout.addWidget(self.plot_button)
        self.setLayout(layout)

    def plot_data(self):
        data = self.tracker.get_category_totals()

        categories = list(data.keys())
        totals = list(data.values())

        plt.figure()
        plt.bar(categories, totals)
        plt.title("Expenses by Category")
        plt.show()
