"""Dashboard page for SKOLLR"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal, Qt


class DashboardPage(QWidget):
    """Dashboard page widget"""
    course_selected = Signal(dict)
    setup_canvas_api = Signal()

    def __init__(self, courses, canvas_api=None):
        super().__init__()
        self.courses = courses
        self.canvas_api = canvas_api

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Dashboard")
        label.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(label)

        layout.addSpacing(10)

        # If no API token set, show setup button
        if not canvas_api:
            layout.addStretch()
            setup_btn = QPushButton("Configure Canvas API Key")
            setup_btn.setMinimumHeight(60)
            setup_btn.setMinimumWidth(200)
            setup_btn.setFont(QFont("Arial", 12, QFont.Bold))
            setup_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 8px;
                    padding: 15px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            setup_btn.clicked.connect(self.setup_canvas_api.emit)
            setup_layout = QVBoxLayout()
            setup_layout.addStretch()
            setup_layout.addWidget(setup_btn, alignment=Qt.AlignCenter)
            setup_layout.addStretch()
            layout.addLayout(setup_layout)
            self.setLayout(layout)
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        container = QWidget()
        self.course_layout = QVBoxLayout(container)
        self.course_layout.setSpacing(10)
        self.course_layout.setAlignment(Qt.AlignTop)

        self.populate_courses()

        scroll.setWidget(container)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def populate_courses(self):
        # Get courses from canvas_api if available
        course_names = []
        if self.canvas_api and hasattr(self.canvas_api, 'courses'):
            # Use courses from Canvas API
            for course in self.canvas_api.courses:
                course_names.append(course.get("name", "Unknown"))
        else:
            # Fallback to passed courses
            for course in self.courses:
                if isinstance(course, dict):
                    name = course.get("course_name", "Unknown Course")
                else:
                    name = str(course)
                course_names.append(name)

        # Calculate adaptive button height based on number and length of courses
        num_courses = len(course_names)
        if num_courses == 0:
            return

        # Calculate base height: longer names = taller buttons
        max_name_length = max(len(name) for name in course_names)
        base_height = max(50, min(25 + max_name_length, 100))

        # Add buttons for each course
        for course_name in course_names:
            btn = QPushButton(course_name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(base_height)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px;
                    background-color: #2c3e50;
                    color: white;
                    border-radius: 8px;
                    text-align: left;
                    white-space: normal;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)

            # For now, emit a dummy course_selected signal
            btn.clicked.connect(lambda checked, name=course_name: self.course_selected.emit(
                {"course_name": name}))

            self.course_layout.addWidget(btn)
