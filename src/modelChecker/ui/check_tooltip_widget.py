from PySide6 import QtWidgets, QtCore
from modelChecker.constants import Severity, SEVERITY_COLORS

INACTIVE_COLOR = "#666666"
MAYA_COLOR = "#00cc00"
USD_COLOR = "#ddaa00"
DEFAULT_SEVERITY_COLOR = "#ffffff"

class CheckTooltipWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, text="", severity=Severity.MILD):
        super().__init__(parent, QtCore.Qt.ToolTip)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setStyleSheet("background-color: #333; color: white; border-radius: 5px; padding: 8px;")
        
        self.layout = QtWidgets.QVBoxLayout(self)

        self.maya_label = QtWidgets.QLabel("Maya")
        self.usd_label = QtWidgets.QLabel("USD")
        
        
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label)
        
        severity_color = SEVERITY_COLORS.get(severity, DEFAULT_SEVERITY_COLOR)
        self.severity_label = QtWidgets.QLabel(severity.name.capitalize())
        self.severity_label.setStyleSheet(f"color: {severity_color}; font-weight: bold;")
        self.layout.addWidget(self.severity_label)
        
        self.setVisible(False)
    
    def set_text(self, text):
        self.label.setText(text)
    
    
    def set_severity(self, severity: Severity):
        """Update the severity label and its color."""
        severity_color = SEVERITY_COLORS.get(severity, DEFAULT_SEVERITY_COLOR)
        self.severity_label.setText(severity.name.capitalize())
        self.severity_label.setStyleSheet(f"color: {severity_color}; font-weight: bold;")
    
    def show_tooltip(self, position):
        self.move(position)
        self.setVisible(True)
    
    def hide_tooltip(self):
        self.setVisible(False)
