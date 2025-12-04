from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout
)
from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont

class CourseDetailPage(QWidget):
    """Displays details for a single course"""

    # Signal to tell the main window to go back
    back_clicked = Signal()

    def __init__(self, course_name, assignments, files):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Header with Back Button ---
        header_layout = QHBoxLayout()

        back_btn = QPushButton("←")
        back_btn.setFixedSize(30, 30)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e; color: white;
                border-radius: 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45627d; }
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)

        title = QLabel(course_name)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: white; margin-left: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # --- Scroll Area ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent;") # Keep transparent for widget look

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(container)
        content_layout.setSpacing(15)

        # 1. Assignments Section
        lbl_hw = QLabel("📝 Upcoming Assignments")
        lbl_hw.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_hw.setStyleSheet("color: #bdc3c7; margin-top: 10px;")
        content_layout.addWidget(lbl_hw)

        if not assignments:
            content_layout.addWidget(QLabel("No upcoming assignments."))
        else:
            for hw in assignments:
                row = QHBoxLayout()
                hw_name = hw.get('assignment_name', 'Unknown')
                hw_due = hw.get('due_at', 'No Date')

                info_lbl = QLabel(f"{hw_name}\nDue: {hw_due}")
                info_lbl.setStyleSheet("font-size: 11px; color: white;")
                row.addWidget(info_lbl)

                link_btn = QPushButton("🔗")
                link_btn.setFixedSize(24, 24)
                link_btn.setCursor(Qt.PointingHandCursor)
                link_btn.setStyleSheet("background-color: #2980b9; border-radius: 4px;")
                link_btn.clicked.connect(lambda _, url=hw.get("url"): self.open_link(url))
                row.addWidget(link_btn)

                content_layout.addLayout(row)

        # 2. Files Section
        lbl_files = QLabel("📁 Course Materials")
        lbl_files.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_files.setStyleSheet("color: #bdc3c7; margin-top: 20px;")
        content_layout.addWidget(lbl_files)

        if not files:
            content_layout.addWidget(QLabel("No files found."))
        else:
            for module in files:
                mod_name = module.get("module_name", "Module")
                mod_lbl = QLabel(f"📂 {mod_name}")
                mod_lbl.setStyleSheet("font-weight: bold; color: #95a5a6; margin-top: 5px;")
                content_layout.addWidget(mod_lbl)

                for f in module.get("files", []):
                    row = QHBoxLayout()
                    f_name = f.get("name", "File")
                    f_lbl = QLabel(f"📄 {f_name}")
                    f_lbl.setStyleSheet("font-size: 11px; color: white; margin-left: 10px;")
                    row.addWidget(f_lbl)

                    link_btn = QPushButton("🔗")
                    link_btn.setFixedSize(24, 24)
                    link_btn.setCursor(Qt.PointingHandCursor)
                    link_btn.setStyleSheet("background-color: #27ae60; border-radius: 4px;")
                    link_btn.clicked.connect(lambda _, url=f.get("url"): self.open_link(url))
                    row.addWidget(link_btn)

                    content_layout.addLayout(row)

        content_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def open_link(self, url):
        if url:
            QDesktopServices.openUrl(QUrl(url))
