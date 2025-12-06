#!/usr/bin/env python3
"""
SKOLLR - Canvas LMS Widget Application
"""

import sys
import os
import concurrent.futures
import requests
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QStackedLayout, QGraphicsOpacityEffect, QStackedWidget,
    QMessageBox
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QMouseEvent, QIcon, QPixmap

from src.ui.dashboard import DashboardPage
from src.ui.analysis import AnalysisPage
from src.ui.course_details import CourseDetailPage
from src.ui.graphs import GraphsPage
from src.ui.settings import SettingsPage
from src.ui.api_key_dialog import ApiKeyDialog
from src.api.canvas_api import CanvasLMSAPI
from dotenv import load_dotenv

load_dotenv()


def save_api_key_to_env(key_name: str, key_value: str):
    """Save API key to .env file automatically"""
    env_path = Path(__file__).parent / ".env"

    # Read existing content
    content = ""
    if env_path.exists():
        with open(env_path, "r") as f:
            content = f.read()

    # Check if key already exists
    lines = content.split("\n") if content else []
    found = False

    for i, line in enumerate(lines):
        if line.startswith(f"{key_name}="):
            lines[i] = f"{key_name}={key_value}"
            found = True
            break

    if not found:
        lines.append(f"{key_name}={key_value}")

    # Write back
    with open(env_path, "w") as f:
        f.write("\n".join(lines))

    # Update os.environ
    os.environ[key_name] = key_value


def validate_canvas_credentials(base_url: str, api_token: str):
    """Return (ok, error_message) after attempting a lightweight Canvas call."""
    base_url = (base_url or "").strip()
    api_token = (api_token or "").strip()
    if not base_url or not api_token:
        return False, "Base URL and API token are required."

    # Ensure scheme
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        base_url = "https://" + base_url

    test_url = base_url.rstrip("/") + "/api/v1/courses"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    params = {"per_page": 1}
    try:
        resp = requests.get(test_url, headers=headers, params=params, timeout=8)
        if resp.status_code == 200:
            return True, ""
        return False, f"Canvas replied with HTTP {resp.status_code}. Check URL/token."
    except requests.exceptions.RequestException as exc:
        return False, f"Network error: {exc}"


class SkollrWidget(QMainWindow):
    """Compact desktop widget for Canvas LMS"""

    def __init__(self, courses, files, assignments, canvas_api=None):
        super().__init__()
        self.dragging = False
        self.drag_position = QPoint()

        self.assignments = assignments
        self.files = files
        self.canvas_api = canvas_api

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
        self.dashboard_stack = QStackedWidget()

        # Page 1: The Course List
        self.dashboard_list = DashboardPage(courses, canvas_api)
        # Connect the signal from DashboardPage to our handler
        self.dashboard_list.course_selected.connect(self.show_course_detail)
        self.dashboard_list.setup_canvas_api.connect(
            self.show_canvas_api_dialog)

        self.dashboard_stack.addWidget(self.dashboard_list)

        # Add the STACK to the tab, not just the page
        self.tabs.addTab(self.dashboard_stack, "Dashboard")
        self.tabs.addTab(AnalysisPage(courses, assignments, files), "Analysis")
        self.tabs.addTab(GraphsPage(), "Graphs")

        self.settings_page = SettingsPage()
        self.settings_page.configure_canvas.connect(self.show_canvas_api_dialog)
        self.tabs.addTab(self.settings_page, "Settings")

        foreground = QWidget()
        foreground.setLayout(main_layout)

        stacked_layout.addWidget(foreground)
        main_container.setLayout(stacked_layout)
        self.setCentralWidget(main_container)

        # Apply initial sizing for the background logo
        self._update_background_logo_size()

    def show_course_detail(self, course_data):
        """Switches the Dashboard tab to show course details"""
        course_name = course_data.get("course_name")

        # 1. Filter Assignments for this course
        # Matches structure from previous canvas_api responses
        c_assigns = next((a["assignments"] for a in self.assignments if a.get(
            "course_name") == course_name), [])

        # 2. Filter Files for this course
        c_files = []
        for f_dict in self.files:
            if course_name in f_dict:
                c_files = f_dict[course_name]
                break

        # 3. Create Detail Page
        detail_page = CourseDetailPage(course_name, c_assigns, c_files)
        detail_page.back_clicked.connect(self.go_back_to_dashboard)

        # 4. Add to stack and show
        self.dashboard_stack.addWidget(detail_page)
        self.dashboard_stack.setCurrentWidget(detail_page)

    def go_back_to_dashboard(self):
        """Removes the detail page and shows the list again"""
        current = self.dashboard_stack.currentWidget()
        if current != self.dashboard_list:
            self.dashboard_stack.removeWidget(current)
            current.deleteLater()
            self.dashboard_stack.setCurrentWidget(self.dashboard_list)

    def show_canvas_api_dialog(self):
        """Show dialog to input Canvas API key and Base URL"""
        dialog = ApiKeyDialog(
            self,
            api_name="Canvas LMS",
            prompt_text="Enter your Canvas LMS API token and institution URL.\nYou can find the API token in Canvas > Account > Settings.",
            fields=[
                ("canvas_base_url", False,
                 "Canvas Base URL (e.g., https://canvas.instructure.com):"),
                ("canvas_api_token", True, "Canvas API Token:")
            ]
        )
        if dialog.exec() == 1:  # QDialog.Accepted == 1
            values = dialog.get_values()
            api_token = values.get("canvas_api_token", "")
            base_url = values.get("canvas_base_url", "")

            ok, err = validate_canvas_credentials(base_url, api_token)
            if not ok:
                QMessageBox.warning(self, "Canvas Connection Failed", err)
                return

            # Save to .env automatically
            save_api_key_to_env("CANVAS_API_TOKEN", api_token)
            save_api_key_to_env("CANVAS_BASE_URL", base_url)

            # Reload the app
            self.close()
            load_dotenv()
            # Restart the app logic
            import subprocess
            subprocess.Popen([sys.executable, __file__])
            QApplication.quit()

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

    api_token = os.environ.get("CANVAS_API_TOKEN")
    api_base_url = f'{os.getenv("CANVAS_BASE_URL", "")}/api/v1'

    courses = []
    assignments = []
    files = []
    canvas_api = None

    if api_token and api_token.strip():
        try:
            canvas_api = CanvasLMSAPI(
                api_token=api_token, base_url=api_base_url)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_courses = executor.submit(
                    canvas_api.all_courses_and_grades)
                future_assignments = executor.submit(
                    canvas_api.all_assignments)
                future_files = executor.submit(canvas_api.all_files)
                courses = future_courses.result()
                assignments = future_assignments.result()
                files = future_files.result()
        except Exception as e:
            print(f"Error loading Canvas data: {e}")
            canvas_api = CanvasLMSAPI(
                api_token=api_token, base_url=api_base_url)

    widget = SkollrWidget(courses=courses, files=files,
                          assignments=assignments, canvas_api=canvas_api)
    widget.show()
    sys.exit(app.exec())
