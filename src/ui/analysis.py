from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QTextEdit, QFrame
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QThread, Signal
from src.ai.gemini import generate_study_tips

class AnalysisWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, course_name, assignments, modules):
        super().__init__()
        self.course_name = course_name
        self.assignments = assignments
        self.modules = modules

    def run(self):
        try:
            tips = generate_study_tips(self.course_name, self.assignments, self.modules)
            self.finished.emit(tips)
        except Exception as e:
            self.error.emit(str(e))

class AnalysisPage(QWidget):
    def __init__(self, courses, assignments, files):
        super().__init__()
        self.courses = courses
        self.assignments = assignments
        self.files = files
        self.workers = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("AI Course Analysis")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        self.layout.addWidget(header)

        sub_header = QLabel("Select a course to generate study tips based on your current assignments and materials.")
        sub_header.setWordWrap(True)
        sub_header.setStyleSheet("color: #bdc3c7; margin-bottom: 10px;")
        self.layout.addWidget(sub_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.courses_layout = QVBoxLayout(container)
        self.courses_layout.setAlignment(Qt.AlignTop)
        self.courses_layout.setSpacing(15)

        self.populate_courses()

        scroll.setWidget(container)
        self.layout.addWidget(scroll)

        self.result_label = QLabel("Analysis Results:")
        self.result_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.result_label.setVisible(False)
        self.layout.addWidget(self.result_label)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setVisible(False)
        self.result_area.setMinimumHeight(200)
        self.result_area.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.layout.addWidget(self.result_area)

    def populate_courses(self):
        if not self.courses:
            self.courses_layout.addWidget(QLabel("No courses available."))
            return

        for course in self.courses:
            c_name = course.get("course_name", "Unknown Course")

            row_widget = QWidget()
            row_layout = QVBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 10)

            lbl = QLabel(c_name)
            lbl.setFont(QFont("Arial", 12))
            lbl.setWordWrap(True)
            row_layout.addWidget(lbl)

            btn = QPushButton("Generate Tips 🪄")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #8e44ad;
                    color: white;
                    border-radius: 6px;
                    padding: 8px;
                    font-weight: bold;
                    text-align: left;
                    padding-left: 15px;
                }
                QPushButton:hover { background-color: #9b59b6; }
                QPushButton:disabled { background-color: #7f8c8d; }
            """)

            btn.clicked.connect(lambda checked, n=c_name, b=btn: self.start_analysis(n, b))

            row_layout.addWidget(btn)

            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("background-color: #34495e;")
            row_layout.addWidget(line)

            self.courses_layout.addWidget(row_widget)

    def start_analysis(self, course_name, button):
        button.setEnabled(False)
        button.setText("Thinking...")
        self.result_label.setVisible(True)
        self.result_label.setText(f"Generating tips for: {course_name}...")
        self.result_area.setVisible(True)
        self.result_area.clear()

        c_assigns = next((a["assignments"] for a in self.assignments if a.get("course_name") == course_name), [])

        c_modules = []
        for f_dict in self.files:
            if course_name in f_dict:
                c_modules = f_dict[course_name]
                break

        worker = AnalysisWorker(course_name, c_assigns, c_modules)
        worker.finished.connect(lambda tips: self.handle_success(tips, button))
        worker.error.connect(lambda err: self.handle_error(err, button))

        self.workers.append(worker)
        worker.start()

    def handle_success(self, tips, button):
        self.result_area.setMarkdown(tips)
        self.result_label.setText("Analysis Results:")
        button.setEnabled(True)
        button.setText("Generate Tips 🪄")

    def handle_error(self, error_msg, button):
        self.result_area.setText(f"Error: {error_msg}")
        button.setEnabled(True)
        button.setText("Retry")
