from PySide6 import QtWidgets, QtCore, QtGui
from modelChecker.constants import SEVERITY_COLORS, PASS_COLOR, INFO_SYMBOL
from modelChecker.ui.check_tooltip_widget import CheckTooltipWidget

class CheckWidget(QtWidgets.QWidget):
    select_error_signal = QtCore.Signal(object)
    run_signal = QtCore.Signal(object)
    fix_signal = QtCore.Signal(object)
    
    def __init__(self, check):
        super().__init__()
        self.check = check()
        self.show_options = False
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        body_widget = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QHBoxLayout(body_widget)
        
        self.main_layout.setSpacing(4)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("padding: 0px; margin: 0px;")
        
        self.info_label = QtWidgets.QLabel(INFO_SYMBOL)
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_label.setFixedWidth(20)
        self.info_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        self.tooltip = CheckTooltipWidget(self, self.check.description, self.check.severity)
        
        self.check_label = QtWidgets.QLabel(self.check.label)
        
        self.settings_widget = QtWidgets.QWidget()
        self.settings_widget.setVisible(False)
        
        self.settings_layout = QtWidgets.QVBoxLayout(self.settings_widget)
        self.settings_layout.addWidget(QtWidgets.QLabel("This is here for sure!!"))
        
        self.enabled = QtWidgets.QCheckBox()
        self.enabled.setCheckState(QtCore.Qt.Checked)
        self.enabled.setMaximumWidth(20)
        
        run_button = QtWidgets.QPushButton("Run")
        run_button.clicked.connect(self.run)
        run_button.setMaximumWidth(40)
        
        fix_button = QtWidgets.QPushButton("Fix")
        fix_button.clicked.connect(self.fix)
        fix_button.setEnabled(self.check.has_fix())
        fix_button.setMaximumWidth(40)
        
        select_error_nodes_button = QtWidgets.QPushButton("Select Error Nodes")
        select_error_nodes_button.clicked.connect(self.select_error)
        select_error_nodes_button.setMaximumWidth(150)
        
        settings_enabled = self.check.has_settings()
        
        label = "\u2699" if settings_enabled else "\u2716"
        settings_button = QtWidgets.QPushButton(label)
        settings_button.setMaximumWidth(40)

        if settings_enabled:
            settings_button.clicked.connect(self._toggle_settings)
        else:
            settings_button.setEnabled(False)
        
        self.body_layout.addWidget(self.info_label) 
        self.body_layout.addWidget(self.check_label)
        self.body_layout.addWidget(self.enabled)
        self.body_layout.addWidget(run_button)
        self.body_layout.addWidget(fix_button)
        self.body_layout.addWidget(select_error_nodes_button)
        self.body_layout.addWidget(settings_button)
        self.main_layout.addWidget(body_widget)
        self.main_layout.addWidget(self.settings_widget)
        
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
