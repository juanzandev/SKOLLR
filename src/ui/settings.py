"""Settings page for SKOLLR"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont


class SettingsPage(QWidget):
    """Settings page widget"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel("Settings")
        label.setFont(QFont("Arial", 14))
        layout.addWidget(label)

        layout.addStretch()
        self.setLayout(layout)
