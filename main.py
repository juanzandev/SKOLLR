#!/usr/bin/env python3
"""
SKOLLR - Canvas LMS Widget Application
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QStackedLayout, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QMouseEvent, QIcon, QPixmap

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

        # Assets (located under src/img)
        base_dir = Path(__file__).parent
        assets_dir = base_dir / "src" / "img"
        self.logo_path = assets_dir / "logo.png"
        self.logo_nofont_path = assets_dir / "logo_nofont.png"

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

        # App icon (taskbar + window)
        if self.logo_nofont_path.exists():
            self.setWindowIcon(QIcon(str(self.logo_nofont_path)))

        # Main container with stacked layout (background + foreground)
        main_container = QWidget()
        stacked_layout = QStackedLayout()
        # Stack all layers so the foreground UI shows above the background logo
        stacked_layout.setStackingMode(QStackedLayout.StackAll)

        # Background logo (centered, low opacity)
        self.bg_label = QLabel()
        self.bg_pixmap = None
        if self.logo_path.exists():
            maybe_pixmap = QPixmap(str(self.logo_path))
            if not maybe_pixmap.isNull():
                self.bg_pixmap = maybe_pixmap
                # Center the logo with a soft opacity so it stays unobtrusive
                self.bg_label.setAlignment(Qt.AlignCenter)
                opacity = QGraphicsOpacityEffect()
                opacity.setOpacity(0.95)
                self.bg_label.setGraphicsEffect(opacity)
        self.bg_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        stacked_layout.addWidget(self.bg_label)

        # Foreground content
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)

        # Tab widget for sections
        self.tabs = QTabWidget()
        # Make tab content backgrounds transparent to show the logo softly
        self.tabs.setStyleSheet(
            "QTabWidget::pane { background: transparent; } QWidget { background: transparent; }")
        main_layout.addWidget(self.tabs)

        # Add 4 sections with separate page classes
        self.tabs.addTab(DashboardPage(), "Dashboard")
        self.tabs.addTab(AnalysisPage(), "Analysis")
        self.tabs.addTab(GraphsPage(), "Graphs")
        self.tabs.addTab(SettingsPage(), "Settings")

        foreground = QWidget()
        foreground.setLayout(main_layout)

        stacked_layout.addWidget(foreground)
        main_container.setLayout(stacked_layout)
        self.setCentralWidget(main_container)

        # Apply initial sizing for the background logo
        self._update_background_logo_size()

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

        # App icon on title bar
        icon_label = QLabel()
        if self.logo_nofont_path.exists():
            icon_pix = QPixmap(str(self.logo_nofont_path))
            if not icon_pix.isNull():
                icon_label.setPixmap(icon_pix.scaled(
                    20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setContentsMargins(0, 0, 6, 0)
        layout.addWidget(icon_label)

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

    def resizeEvent(self, event):
        """Keep the background logo at ~2/3 of the window width."""
        self._update_background_logo_size()
        super().resizeEvent(event)

    def _update_background_logo_size(self):
        if not self.bg_pixmap:
            return
        target_width = int(self.width() * (2 / 3))
        if target_width <= 0:
            return
        scaled = self.bg_pixmap.scaled(
            target_width,
            target_width,  # height is constrained by aspect ratio below
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.bg_label.setPixmap(scaled)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SkollrWidget()
    widget.show()
    sys.exit(app.exec())
