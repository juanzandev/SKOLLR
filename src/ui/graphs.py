"""Graphs page for SKOLLR"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont


class GraphsPage(QWidget):
    """Graphs page widget"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel("Graphs")
        label.setFont(QFont("Arial", 14))
        layout.addWidget(label)

        layout.addStretch()
        self.setLayout(layout)
