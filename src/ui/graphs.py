"""Graphs page for SKOLLR"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QUrl
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("[INFO] QWebEngineView not available, using matplotlib fallback")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure

import plotly.graph_objects as go
import tempfile
import os


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
            no_data = QLabel(
                "No course data available.\nConfigure Canvas API in Settings to see graphs.")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #7f8c8d; padding: 40px;")
            layout.addWidget(no_data)

        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _create_grade_bar_chart(self):
        """Create an interactive bar chart showing course grades"""
        # Filter courses with grades
        courses_with_grades = [
            c for c in self.courses if c.get('current_percentage')]

        if not WEBENGINE_AVAILABLE:
            return self._create_fallback_label("Install PySide6-WebEngine for interactive graphs")

        web_view = QWebEngineView()
        web_view.setMinimumHeight(400)

        if courses_with_grades:
            # Prepare data
            names = [c['course_name'] for c in courses_with_grades]
            scores = [c['current_percentage'] for c in courses_with_grades]

            # Create interactive bar chart
            fig = go.Figure(data=[
                go.Bar(
                    y=names,
                    x=scores,
                    orientation='h',
                    marker=dict(
                        color=scores,
                        colorscale='Blues',
                        line=dict(color='#2c3e50', width=1)
                    ),
                    text=[f'{s:.1f}%' for s in scores],
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Grade: %{x:.1f}%<extra></extra>'
                )
            ])

            fig.update_layout(
                title=dict(text='Course Grades', font=dict(
                    size=16, color='#2c3e50')),
                xaxis=dict(title='Grade (%)', range=[
                           0, 100], gridcolor='#ecf0f1'),
                yaxis=dict(title='', automargin=True),
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=50, b=50),
                height=max(300, len(courses_with_grades) * 40)
            )

            html = fig.to_html(include_plotlyjs='cdn')
        else:
            html = '<html><body style="display:flex;align-items:center;justify-content:center;height:100%;font-family:Arial;color:#7f8c8d;">No grade data available</body></html>'

        web_view.setHtml(html)
        return web_view

    def _create_fallback_label(self, message):
        """Create a fallback label when WebEngine is not available"""
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        return label

    def _create_grade_pie_chart(self):
        """Create an interactive pie chart showing grade distribution"""
        # Count letter grades
        grade_counts = {}
        for course in self.courses:
            grade = course.get('current_grade')
            if grade:
                grade_counts[grade] = grade_counts.get(grade, 0) + 1

        if not WEBENGINE_AVAILABLE:
            return self._create_fallback_label("Install PySide6-WebEngine for interactive graphs")

        web_view = QWebEngineView()
        web_view.setMinimumHeight(400)

        if grade_counts:
            labels = list(grade_counts.keys())
            sizes = list(grade_counts.values())

            # Create interactive pie chart
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=sizes,
                    marker=dict(
                        colors=['#2ecc71', '#3498db',
                            '#f39c12', '#e74c3c', '#95a5a6'],
                        line=dict(color='white', width=2)
                    ),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
                    hole=0.3  # Make it a donut chart
                )
            ])

            fig.update_layout(
                title=dict(text='Grade Distribution',
                           font=dict(size=16, color='#2c3e50')),
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=50, b=20),
                height=400,
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom',
                            y=-0.1, xanchor='center', x=0.5)
            )

            html = fig.to_html(include_plotlyjs='cdn')
        else:
            html = '<html><body style="display:flex;align-items:center;justify-content:center;height:100%;font-family:Arial;color:#7f8c8d;">No letter grades available</body></html>'

        web_view.setHtml(html)
        return web_view
