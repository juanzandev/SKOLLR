"""Settings page for SKOLLR"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal, Qt


class SettingsPage(QWidget):
    """Settings page widget"""

    configure_canvas = Signal()  # Signal to open Canvas credentials dialog

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        label = QLabel("Settings")
        label.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(label)

        subtitle = QLabel("Canvas connection")
        subtitle.setFont(QFont("Arial", 12))
        layout.addWidget(subtitle)

        # Single button to edit both Base URL and API token
        btn = QPushButton("Edit Canvas Base URL & API Token")
        btn.setMinimumHeight(46)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 10px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            """
        )
        btn.clicked.connect(self.configure_canvas.emit)
        layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)
