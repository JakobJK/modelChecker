from PySide6 import QtWidgets
from modelChecker.constants import EXPANDED_LABEL, COLLAPSED_LABEL
from modelChecker.ui.check_widget import CheckWidget

class CategoryWidget(QtWidgets.QWidget):
    def __init__(self, category):
        super().__init__()
        self.expanded = True
        
        category_layout = QtWidgets.QVBoxLayout(self)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(0)
        
        category_header_widget = QtWidgets.QWidget()
        category_header_layout = QtWidgets.QHBoxLayout(category_header_widget)
        category_header_layout.setContentsMargins(0, 0, 0, 0)
        category_header_layout.setSpacing(0)
        
        self.category_header_button = QtWidgets.QPushButton(category)
        
        self.expand_button = QtWidgets.QPushButton(EXPANDED_LABEL)
        self.expand_button.setMaximumWidth(50)
        
        category_header_layout.addWidget(self.category_header_button)
        category_header_layout.addWidget(self.expand_button)
        
        self.category_header_button.clicked.connect(self.toggle_checks)
        
        self.category_body_widget = QtWidgets.QWidget()
        self.category_body_layout = QtWidgets.QVBoxLayout(self.category_body_widget)
        self.category_body_layout.setContentsMargins(0, 0, 0, 0)
        self.category_body_layout.setSpacing(0)
        
        category_layout.addWidget(category_header_widget)
        category_layout.addWidget(self.category_body_widget)
    
    def add_check(self, widget):
        self.category_body_layout.addWidget(widget)
        
    def toggle_display(self):
        self.expanded = not self.expanded
        label = EXPANDED_LABEL if self.expanded else COLLAPSED_LABEL
        self.category_body_widget.setVisible(self.expanded)
        self.expand_button.setText(label)
    
    def toggle_checks(self):
        category_widgets = []
        unchecked_widgets = []

        for i in range(self.category_body_layout.count()):
            check_widget = self.category_body_layout.itemAt(i).widget()
            if isinstance(check_widget, CheckWidget):
                category_widgets.append(check_widget)
                if not check_widget.is_checked():
                    unchecked_widgets.append(check_widget)

        should_check = len(unchecked_widgets) > 0

        for widget in category_widgets:
            widget.set_checked(should_check)
