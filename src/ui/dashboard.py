"""Dashboard page for SKOLLR"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont


class DashboardPage(QWidget):
    """Dashboard page widget"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel("Dashboard")
        label.setFont(QFont("Arial", 14))
        layout.addWidget(label)

        layout.addStretch()
        self.setLayout(layout)
