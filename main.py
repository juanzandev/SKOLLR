#!/usr/bin/env python3
"""
SKOLLR - Canvas LMS Widget Application
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QMouseEvent

from src.ui.dashboard import DashboardPage
from src.ui.analysis import AnalysisPage
from src.ui.graphs import GraphsPage
from src.ui.settings import SettingsPage


class SkollrWidget(QMainWindow):
    """Compact desktop widget for Canvas LMS"""

    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_position = QPoint()

        # Window setup
        self.setWindowTitle("SKOLLR")
        self.setGeometry(100, 100, 400, 600)
        self.setMinimumSize(350, 500)
        self.setMaximumSize(600, 800)

        # Window flags: borderless, stay at bottom, semi-transparent
        self.setWindowFlags(
            self.windowFlags() |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint
        )
        self.setWindowOpacity(0.95)

        # Main container
        main_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)

        # Tab widget for sections
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Add 4 sections with separate page classes
        self.tabs.addTab(DashboardPage(), "Dashboard")
        self.tabs.addTab(AnalysisPage(), "Analysis")
        self.tabs.addTab(GraphsPage(), "Graphs")
        self.tabs.addTab(SettingsPage(), "Settings")

        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

    def _create_title_bar(self) -> QWidget:
        """Create custom draggable title bar with minimize/close buttons"""
        title_bar = QWidget()
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border-bottom: 1px solid #34495e;
            }
        """)
        title_bar.setMinimumHeight(40)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 5, 5)

        # Title
        title_label = QLabel("SKOLLR")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_label.setFont(QFont("Arial", 10))
        layout.addWidget(title_label)
        layout.addStretch()

        # Minimize button
        minimize_btn = QPushButton("−")
        minimize_btn.setMaximumWidth(50)
        minimize_btn.setMaximumHeight(30)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45627d; }
        """)
        minimize_btn.clicked.connect(self.showMinimized)
        layout.addWidget(minimize_btn)

        # Close button
        close_btn = QPushButton("×")
        close_btn.setMaximumWidth(100)
        close_btn.setMaximumHeight(30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        title_bar.setLayout(layout)
        return title_bar

    def mousePressEvent(self, event: QMouseEvent):
        """Handle dragging from title bar"""
        if event.position().y() < 40:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - \
                self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Move window while dragging"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop dragging"""
        self.dragging = False
        super().mouseReleaseEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SkollrWidget()
    widget.show()
    sys.exit(app.exec())
