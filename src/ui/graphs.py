"""Graphs page for SKOLLR"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

# Matplotlib imports for embedding in PySide6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas widget for embedding charts"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class GraphsPage(QWidget):
    """Graphs page widget"""

    def __init__(self, courses=None):
        super().__init__()
        self.courses = courses or []
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        label = QLabel("Grade Analytics")
        label.setFont(QFont("Arial", 18, QFont.Bold))
        main_layout.addWidget(label)

        # Scrollable area for multiple graphs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Add graphs if we have course data
        if self.courses:
            # Example 1: Bar chart of grades
            layout.addWidget(self._create_grade_bar_chart())
            
            # Example 2: Pie chart of grade distribution
            layout.addWidget(self._create_grade_pie_chart())
        else:
            no_data = QLabel("No course data available.\nConfigure Canvas API in Settings to see graphs.")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #7f8c8d; padding: 40px;")
            layout.addWidget(no_data)
        
        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _create_grade_bar_chart(self):
        """Create a bar chart showing course grades"""
        canvas = MplCanvas(self, width=5, height=3, dpi=100)
        
        # Filter courses with grades
        courses_with_grades = [c for c in self.courses if c.get('current_percentage')]
        
        if courses_with_grades:
            # Shorten course names for display
            names = [c['course_name'][:30] + '...' if len(c['course_name']) > 30 
                    else c['course_name'] for c in courses_with_grades]
            scores = [c['current_percentage'] for c in courses_with_grades]
            
            canvas.axes.barh(names, scores, color='#3498db')
            canvas.axes.set_xlabel('Grade (%)', fontsize=10)
            canvas.axes.set_title('Course Grades', fontsize=12, fontweight='bold')
            canvas.axes.set_xlim(0, 100)
            
            # Add percentage labels on bars
            for i, v in enumerate(scores):
                canvas.axes.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=8)
            
            canvas.axes.tick_params(axis='both', labelsize=8)
            canvas.figure.tight_layout()
        else:
            canvas.axes.text(0.5, 0.5, 'No grade data available', 
                           ha='center', va='center', fontsize=12)
            canvas.axes.set_xticks([])
            canvas.axes.set_yticks([])
        
        return canvas

    def _create_grade_pie_chart(self):
        """Create a pie chart showing grade distribution"""
        canvas = MplCanvas(self, width=5, height=3, dpi=100)
        
        # Count letter grades
        grade_counts = {}
        for course in self.courses:
            grade = course.get('current_grade')
            if grade:
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        if grade_counts:
            labels = list(grade_counts.keys())
            sizes = list(grade_counts.values())
            colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6']
            
            canvas.axes.pie(sizes, labels=labels, autopct='%1.0f%%', 
                          colors=colors[:len(labels)], startangle=90)
            canvas.axes.set_title('Grade Distribution', fontsize=12, fontweight='bold')
            canvas.figure.tight_layout()
        else:
            canvas.axes.text(0.5, 0.5, 'No letter grades available', 
                           ha='center', va='center', fontsize=12)
            canvas.axes.set_xticks([])
            canvas.axes.set_yticks([])
        
        return canvas
