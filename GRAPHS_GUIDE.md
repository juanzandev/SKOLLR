# How to Add Graphs to SKOLLR

## Overview
The Graphs page uses `matplotlib` with PySide6 integration. Charts are embedded directly in the Qt widget using `FigureCanvasQTAgg`.

## Current Implementation
Two example graphs are provided:
1. **Horizontal Bar Chart** - Shows course grades as percentages
2. **Pie Chart** - Shows distribution of letter grades (A, B, C, etc.)

## Adding New Graphs

### Step 1: Create a new chart method in `src/ui/graphs.py`

```python
def _create_your_chart_name(self):
    """Description of what this chart shows"""
    canvas = MplCanvas(self, width=5, height=3, dpi=100)
    
    # Your data processing here
    # Example: Extract data from self.courses
    
    # Create the chart
    canvas.axes.plot(x_data, y_data)  # or .bar(), .scatter(), etc.
    canvas.axes.set_xlabel('X Label')
    canvas.axes.set_ylabel('Y Label')
    canvas.axes.set_title('Chart Title', fontsize=12, fontweight='bold')
    canvas.figure.tight_layout()
    
    return canvas
```

### Step 2: Add the chart to the layout in `__init__`

```python
if self.courses:
    layout.addWidget(self._create_grade_bar_chart())
    layout.addWidget(self._create_grade_pie_chart())
    layout.addWidget(self._create_your_chart_name())  # Add here
```

## Common Chart Types

### Line Chart
```python
canvas.axes.plot(x_values, y_values, marker='o', color='#3498db')
canvas.axes.set_xlabel('Week')
canvas.axes.set_ylabel('Grade')
```

### Bar Chart (Vertical)
```python
canvas.axes.bar(categories, values, color='#2ecc71')
```

### Scatter Plot
```python
canvas.axes.scatter(x_data, y_data, alpha=0.6, s=100, color='#e74c3c')
```

### Stacked Bar Chart
```python
canvas.axes.bar(x, y1, label='Category 1')
canvas.axes.bar(x, y2, bottom=y1, label='Category 2')
canvas.axes.legend()
```

### Multiple Lines
```python
canvas.axes.plot(x, y1, label='Course 1', marker='o')
canvas.axes.plot(x, y2, label='Course 2', marker='s')
canvas.axes.legend()
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

### Font Sizes
- Title: `fontsize=12, fontweight='bold'`
- Labels: `fontsize=10`
- Tick labels: `labelsize=8`

### Dark Theme Compatible
```python
canvas.axes.set_facecolor('#2c3e50')  # Dark background
canvas.axes.tick_params(colors='white')
canvas.axes.spines['bottom'].set_color('white')
```

## Example: Assignment Due Dates Timeline

```python
def _create_assignment_timeline(self):
    """Show upcoming assignments on a timeline"""
    canvas = MplCanvas(self, width=6, height=3, dpi=100)
    
    # Collect assignment data
    dates = []
    courses = []
    
    for assignment in self.assignments:
        if assignment.get('due_at'):
            dates.append(assignment['due_at'])
            courses.append(assignment['course_name'])
    
    # Create timeline
    canvas.axes.scatter(dates, courses, s=100, color='#e74c3c')
    canvas.axes.set_xlabel('Due Date')
    canvas.axes.set_title('Upcoming Assignments', fontsize=12, fontweight='bold')
    canvas.figure.autofmt_xdate()  # Rotate date labels
    canvas.figure.tight_layout()
    
    return canvas
```

## Using Plotly Instead

If you prefer interactive Plotly charts:

1. Install: `pip install plotly kaleido`
2. Generate HTML:
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Bar(x=names, y=values)])
html = fig.to_html(include_plotlyjs='cdn')
```
3. Display in QWebEngineView

## Testing Your Graphs

Run the app with course data:
```bash
python main.py
```

Navigate to the "Graphs" tab to see your charts.

## Troubleshooting

**No graphs showing?**
- Check if courses data is being passed: `print(len(self.courses))`
- Verify Canvas API is configured in Settings
- Check terminal for matplotlib errors

**Graph too small/large?**
- Adjust canvas size: `MplCanvas(self, width=6, height=4, dpi=100)`
- Modify in `_create_your_chart_name()`

**Colors not showing?**
- Ensure color strings are valid hex codes
- Use `color='#3498db'` format
