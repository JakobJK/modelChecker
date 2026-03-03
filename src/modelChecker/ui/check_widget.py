from PySide6 import QtWidgets, QtCore, QtGui

from typing import Type

from modelChecker.constants import SEVERITY_COLORS, PASS_COLOR, INFO_SYMBOL
from modelChecker.ui.check_tooltip_widget import CheckTooltipWidget
from modelChecker.validation_check_base import ValidationCheckBase

class CheckWidget(QtWidgets.QWidget):
    select_error_signal = QtCore.Signal(object)
    run_signal = QtCore.Signal(object)
    fix_signal = QtCore.Signal(object)
    
    def __init__(self, check: Type[ValidationCheckBase]):
        super().__init__()
        self.check = check()
        self.show_options = False
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.info_label = QtWidgets.QLabel(INFO_SYMBOL)
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        self.tooltip = CheckTooltipWidget(self, self.check.description, self.check.severity)
        
        self.check_label = QtWidgets.QLabel(self.check.label)
        
        self.enabled = QtWidgets.QCheckBox()
        self.enabled.setCheckState(QtCore.Qt.Checked)
        
        run_button = QtWidgets.QPushButton("Run")
        fix_button = QtWidgets.QPushButton("Fix")
        select_error_nodes_button = QtWidgets.QPushButton("Select Error Nodes")

        run_button.clicked.connect(self.run)
        fix_button.clicked.connect(self.fix)
        select_error_nodes_button.clicked.connect(self.select_error)
        
        fix_button.setEnabled(self.check.has_fix())
        

        layout.addWidget(self.info_label) 
        layout.addWidget(self.check_label)
        layout.addStretch()
        layout.addWidget(self.enabled)
        layout.addWidget(run_button)
        layout.addWidget(fix_button)
        layout.addWidget(select_error_nodes_button)
        
        self.info_label.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if obj == self.info_label:
            if event.type() == QtCore.QEvent.Enter:
                self._show_tooltip()
            elif event.type() == QtCore.QEvent.Leave:
                self._hide_tooltip()
        return super().eventFilter(obj, event)
    
    def _show_tooltip(self):
        pos = self.info_label.mapToGlobal(self.info_label.rect().bottomRight())
        self.tooltip.show_tooltip(pos)
    
    def _hide_tooltip(self):
        self.tooltip.hide_tooltip()
    
    def _toggle_settings(self):
        self.settings_widget.setVisible(not self.settings_widget.isVisible())
        
    def update_ui(self, has_error=False):
        if has_error:
            color = SEVERITY_COLORS.get(self.check.severity, "#000000")
            self.check_label.setStyleSheet(f'background-color: {color}')
        else:
            self.check_label.setStyleSheet(f'background-color: {PASS_COLOR}')
            
    def reset_ui(self):
        self.check_label.setStyleSheet('background-color: none')
        
    def set_status(self, status, should_hide):
        self.setEnabled(status)
        self.setVisible(status or should_hide)

    def is_checked(self) -> bool:
        return self.enabled.isChecked()
    
    def set_checked(self, check: bool):
        self.enabled.setChecked(check)
    
    def select_error(self):
        self.select_error_signal.emit(self)
    
    def fix(self):
        self.fix_signal.emit(self)
    
    def run(self):
        self.run_signal.emit(self)
