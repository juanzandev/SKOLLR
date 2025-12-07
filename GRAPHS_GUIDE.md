# How to Add Graphs to SKOLLR

## Overview

The Graphs page uses **Plotly** for interactive visualizations, embedded using `QWebEngineView`. Charts are rendered as HTML with interactive hover tooltips, zoom, and pan capabilities.

## Current Implementation

Two example graphs are provided:

1. **Horizontal Bar Chart** - Shows course grades as percentages (interactive hover)
2. **Donut Chart** - Shows distribution of letter grades (A, B, C, etc.)

## Adding New Graphs

### Step 1: Create a new chart method in `src/ui/graphs.py`

```python
def _create_your_chart_name(self):
    """Description of what this chart shows"""
    # Check if WebEngine is available
    if not WEBENGINE_AVAILABLE:
        return self._create_fallback_label("WebEngine not available for interactive charts")

    web_view = QWebEngineView()
    web_view.setMinimumHeight(400)

    # Process your data from self.courses
    # Example: course_names = [c['course_name'] for c in self.courses]

    # Create Plotly figure
    import plotly.graph_objects as go
    fig = go.Figure()

    # Add trace (bar, scatter, line, etc.)
    fig.add_trace(go.Bar(
        x=your_x_data,
        y=your_y_data,
        marker=dict(color='#3498db'),
        hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title='Your Chart Title',
        xaxis_title='X Axis Label',
        yaxis_title='Y Axis Label',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial', size=12, color='#2c3e50')
    )

    # Render to HTML
    html = fig.to_html(include_plotlyjs='cdn')
    web_view.setHtml(html)
    return web_view
```

### Step 2: Add the chart to the layout in `__init__`

```python
if self.courses:
    layout.addWidget(self._create_grade_bar_chart())
    layout.addWidget(self._create_grade_pie_chart())
    layout.addWidget(self._create_your_chart_name())  # Add here
```

## Common Chart Types

### Bar Chart (Horizontal)

```python
fig.add_trace(go.Bar(
    y=categories,  # Horizontal bars
    x=values,
    orientation='h',
    marker=dict(color='#2ecc71')
))
```

### Line Chart

```python
fig.add_trace(go.Scatter(
    x=x_values,
    y=y_values,
    mode='lines+markers',
    line=dict(color='#3498db', width=2),
    marker=dict(size=8)
))
```

### Scatter Plot

```python
fig.add_trace(go.Scatter(
    x=x_data,
    y=y_data,
    mode='markers',
    marker=dict(size=10, color='#e74c3c', opacity=0.6)
))
```

### Pie/Donut Chart

```python
fig.add_trace(go.Pie(
    labels=categories,
    values=counts,
    hole=0.4,  # 0.4 for donut, 0 for pie
    marker=dict(colors=['#3498db', '#2ecc71', '#f39c12'])
))
```

### Multiple Lines

```python
fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='Series 1'))
fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Series 2'))
```

## Available Data in self.courses

Each course is a dictionary with:

```python
{
    'course_name': str,           # Full course name
    'current_grade': str or None, # Letter grade (A, B, C, etc.)
    'current_percentage': float or None  # Numeric percentage
}
```

## Styling Tips

### Colors

Use these professional colors:

- Blue: `#3498db`
- Green: `#2ecc71`
- Orange: `#f39c12`
- Red: `#e74c3c`
- Gray: `#95a5a6`
- Purple: `#9b59b6`
- Teal: `#1abc9c`

### Layout Options

```python
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot area
    font=dict(family='Arial', size=12, color='#2c3e50'),
    height=400,
    showlegend=True,
    hovermode='closest'  # or 'x', 'y', 'x unified'
)
```

### Interactive Features

Plotly charts automatically include:

- **Hover tooltips** - Customize with `hovertemplate`
- **Zoom** - Box select or scroll to zoom
- **Pan** - Click and drag
- **Download** - Save as PNG from toolbar
- **Toggle traces** - Click legend items to hide/show

## Example: Assignment Due Dates Timeline

```python
def _create_assignment_timeline(self):
    """Show upcoming assignments on a timeline"""
    if not WEBENGINE_AVAILABLE:
        return self._create_fallback_label("WebEngine not available")

    web_view = QWebEngineView()
    web_view.setMinimumHeight(400)

    # Collect assignment data
    from datetime import datetime
    dates = []
    courses = []

    for assignment in self.assignments:
        if assignment.get('due_at'):
            dates.append(datetime.fromisoformat(assignment['due_at']))
            courses.append(assignment['course_name'])

    # Create Plotly figure
    import plotly.graph_objects as go
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=courses,
        mode='markers',
        marker=dict(size=12, color='#e74c3c'),
        hovertemplate='<b>%{y}</b><br>Due: %{x}<extra></extra>'
    ))

    fig.update_layout(
        title='Upcoming Assignments',
        xaxis_title='Due Date',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial', size=12, color='#2c3e50')
    )

    html = fig.to_html(include_plotlyjs='cdn')
    web_view.setHtml(html)
    return web_view
```

## Testing Your Graphs

Run the app with course data:

```bash
python main.py
```

Navigate to the "Graphs" tab to see your interactive charts. Hover over chart elements to see detailed tooltips!

## Troubleshooting

**No graphs showing?**

- Check if courses data is being passed: `print(len(self.courses))`
- Verify Canvas API is configured in Settings
- Check debug output: Canvas data loading logs appear in terminal

**"WebEngine not available" message?**

- WebEngine is included with PySide6 6.9.2+
- Try: `python -c "from PySide6.QtWebEngineWidgets import QWebEngineView"`
- If import fails, reinstall: `pip install --force-reinstall PySide6==6.9.2`

**Graph too small/large?**

- Adjust height in layout: `fig.update_layout(height=500)`
- Modify minimum height: `web_view.setMinimumHeight(450)`

**Colors not showing?**

- Ensure color strings are valid hex codes: `#3498db`
- Plotly also accepts CSS names: `'dodgerblue'`, `'crimson'`

**Interactive features not working?**

- Check if HTML rendered: View page source in browser
- Verify `include_plotlyjs='cdn'` loads correctly
- Test internet connection (CDN requirement)
