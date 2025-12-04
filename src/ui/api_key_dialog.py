"""Dialog for API key input"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtGui import QFont


class ApiKeyDialog(QDialog):
    """Dialog to prompt user for API keys with censored input"""

    def __init__(self, parent=None, api_name="API", prompt_text="", fields=None):
        """
        Initialize the dialog.
        fields: list of tuples (field_name, is_password, label_text)
                e.g., [("api_token", True, "API Token:"), ("base_url", False, "Base URL:")]
        """
        super().__init__(parent)
        self.setWindowTitle(f"{api_name} Setup")
        self.setModal(True)
        self.setMinimumWidth(450)

        self.fields_dict = {}  # Store input fields by name

        layout = QVBoxLayout()

        # Title
        title = QLabel(f"Configure {api_name}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # Description
        if prompt_text:
            desc = QLabel(prompt_text)
            desc.setWordWrap(True)
            layout.addWidget(desc)

        # Dynamic fields
        if fields:
            for field_name, is_password, label_text in fields:
                layout.addWidget(QLabel(label_text))
                field_input = QLineEdit()
                if is_password:
                    field_input.setEchoMode(QLineEdit.Password)
                field_input.setMinimumHeight(35)
                layout.addWidget(field_input)
                self.fields_dict[field_name] = field_input

        # Buttons
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        submit_btn = QPushButton("Save")
        submit_btn.clicked.connect(self.accept)
        btn_layout.addWidget(submit_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_values(self):
        """Return dict of field names and their values"""
        return {name: field.text().strip() for name, field in self.fields_dict.items()}
