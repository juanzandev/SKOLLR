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

    def __init__(self, courses=None, assignments=None):
        super().__init__()
        self.courses = courses or []
        self.assignments = assignments or []

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

            layout.addWidget(self._create_grade_vs_time_chart())
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
    
    def _create_grade_vs_time_chart(self):
        """Plot running grade % vs time for each course, from earliest assignment date → now.
        - Assumes self.assignments is a list of { "course_name": str, "assignments": [ ... ] }
        - Each assignment: { "assignment_name": str, "due_at": str, "total_points": float, "score": float or None }
        - Missing 'score' is treated as 0 (changeable; comments below show how to ignore ungraded).
        """
        if not WEBENGINE_AVAILABLE:
            return self._create_fallback_label("WebEngine not available for interactive charts")

        from datetime import datetime

        web_view = QWebEngineView()
        web_view.setMinimumHeight(480)

        # -------------------------
        # Helper: parse Canvas-style date
        # Example: "Dec 09, 2025 11:59 PM Central Standard Time"
        # Keep first 5 tokens -> "Dec 09, 2025 11:59 PM"
        # -------------------------
        def parse_canvas_date(raw):
            if not raw:
                return None
            parts = raw.split()
            if len(parts) < 5:
                return None
            trimmed = " ".join(parts[:5])
            try:
                return datetime.strptime(trimmed, "%b %d, %Y %I:%M %p")
            except Exception:
                return None

        # -------------------------
        # Collect and normalize input
        # -------------------------
        # course_points: course_name -> list of (due_datetime, earned, total)
        course_points = {}
        earliest = None

        for course in self.assignments:
            cname = course.get("course_name", "Unknown Course")
            entries = []

            for a in course.get("assignments", []):
                raw_due = a.get("due_at")
                dt = parse_canvas_date(raw_due)
                if dt is None:
                    continue

                total = a.get("total_points")
                # skip if no total_points
                if total is None:
                    continue

                # if the assignment has an explicit score use it, otherwise treat as 0
                # (If you prefer to ignore ungraded items, set `earned = None` and handle below)
                earned = a.get("score", 0.0)
                try:
                    total = float(total)
                except Exception:
                    continue
                try:
                    earned = float(earned) if earned is not None else 0.0
                except Exception:
                    earned = 0.0

                entries.append((dt, earned, total))

                if earliest is None or dt < earliest:
                    earliest = dt

            if entries:
                # sort per-course
                entries.sort(key=lambda x: x[0])
                course_points[cname] = entries

        # If there's no parsed date at all, fallback single point
        if earliest is None:
            from datetime import datetime
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[datetime.now()], y=[0], mode="markers", name="No data"))
            fig.update_layout(title="Running Grade vs Time (Per Course)", xaxis_title="Date", yaxis_title="Grade (%)")
            html = fig.to_html(include_plotlyjs="cdn")
            web_view.setHtml(html)
            return web_view

        # Global timeline: all unique assignment dates across all courses, plus "now" (end)
        now = datetime.now()
        all_dates = set()
        for entries in course_points.values():
            for dt, _, _ in entries:
                all_dates.add(dt)
        all_dates.add(now)
        timeline = sorted(all_dates)

        # -------------------------
        # For each course, compute grade at each timestamp in `timeline`.
        # grade(t) uses assignments with due <= t.
        # -------------------------
        traces = []
        for cname, entries in course_points.items():
            # entries already sorted by date
            idx = 0
            cumulative_earned = 0.0
            cumulative_total = 0.0
            x_vals = []
            y_vals = []

            # Walk timeline in order; advance through entries as timeline progresses
            for t in timeline:
                # include all entries whose due <= t
                while idx < len(entries) and entries[idx][0] <= t:
                    dt_e, earned_e, total_e = entries[idx]
                    # treat earned_e as 0 if None (we already set it to 0 above)
                    if earned_e is None:
                        # if you prefer to IGNORE ungraded items, comment the next line out
                        earned_add = 0.0
                    else:
                        earned_add = earned_e
                    cumulative_earned += earned_add
                    cumulative_total += total_e
                    idx += 1

                # compute grade only if there's any available points up to t
                if cumulative_total > 0:
                    grade_pct = (cumulative_earned / cumulative_total) * 100.0
                    # clamp to [0,100] just in case
                    grade_pct = max(0.0, min(100.0, grade_pct))
                    x_vals.append(t)
                    y_vals.append(grade_pct)
                else:
                    # no available points yet -> append None so Plotly leaves a gap
                    x_vals.append(t)
                    y_vals.append(None)

            # If course never had any available points, skip it
            if all(v is None for v in y_vals):
                continue

            traces.append({
                "name": cname,
                "x": x_vals,
                "y": y_vals
            })

        # -------------------------
        # Build Plotly figure with one trace per course
        # and a dropdown to select single course or show all
        # -------------------------
        fig = go.Figure()

        for t in traces:
            fig.add_trace(go.Scatter(x=t["x"], y=t["y"], mode="lines+markers", name=t["name"], connectgaps=False))

        # Create dropdown buttons:
        # - one button per course that shows only that course
        # - one "All courses" button
        visibility_all = [True] * len(traces)
        buttons = []

        # "All" button
        buttons.append(dict(
            label="All courses",
            method="update",
            args=[{"visible": visibility_all},
                {"title": "Running Grade vs Time — All courses"}]
        ))

        # Individual course buttons
        for i, t in enumerate(traces):
            vis = [False] * len(traces)
            vis[i] = True
            buttons.append(dict(
                label=t["name"],
                method="update",
                args=[{"visible": vis},
                    {"title": f"Running Grade vs Time — {t['name']}"}]
            ))

        fig.update_layout(
            updatemenus=[dict(active=0, buttons=buttons, x=0.0, y=1.15, xanchor="left")],
            title="Running Grade vs Time — All courses",
            xaxis_title="Date",
            yaxis_title="Grade (%)",
            height=520,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Arial', size=12, color='#2c3e50'),
            yaxis=dict(range=[0, 100])
        )

        # Improve x-axis range: from earliest -> now
        fig.update_xaxes(range=[earliest, now])

        # Render and return
        html = fig.to_html(include_plotlyjs="cdn")
        web_view.setHtml(html)
        return web_view
