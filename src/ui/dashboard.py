"""Dashboard page for SKOLLR"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal, Qt


class DashboardPage(QWidget):
    """Dashboard page widget"""
    course_selected = Signal(dict)

    def __init__(self, courses):
        super().__init__()
        self.courses = courses

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Dashboard")
        label.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(label)

        layout.addSpacing(10)

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

    def populate_courses(self):
        for course in self.courses:
            if isinstance(course, dict):
                name = course.get("course_name", "Unknown Course")
                grade = course.get("current_grade")
                percent = course.get("current_percentage")
            else:
                name = str(course)
                grade = None
                percent = None

            if grade and percent:
                display_text = f"{name} | {grade} - {percent}%"
            else:
                display_text = name

            btn = QPushButton(display_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 15px;
                    background-color: #2c3e50;
                    color: white;
                    border-radius: 8px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)

            btn.clicked.connect(lambda _, c=course: self.course_selected.emit(c))

            self.course_layout.addWidget(btn)
