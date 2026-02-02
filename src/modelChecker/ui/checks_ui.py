from PySide6 import QtWidgets, QtCore

from modelChecker.checks import all_checks

from modelChecker.ui.check_widget import CheckWidget
from modelChecker.ui.category_widget import CategoryWidget

class ChecksUI(QtWidgets.QWidget):
    select_error_signal = QtCore.Signal(object)
    run_signal = QtCore.Signal(object)
    fix_signal = QtCore.Signal(object)
    uncheck_passed_signal = QtCore.Signal()
    
    def __init__(self):
        super().__init__()
        
        self.categories = {}
        self.checks = {}
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0) 

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)

        categories = sorted({x.category for x in all_checks})
        
        for category in categories:
            category_widget = CategoryWidget(category)
            self.categories[category] = category_widget
            self.content_layout.addWidget(category_widget)
        
        sorted_checks = sorted(all_checks, key=lambda x: x.label)
        
        for check in sorted_checks:
            check_widget = CheckWidget(check)
            self.checks[check.name] = check_widget
            self.categories[check.category].add_check(check_widget)
            check_widget.select_error_signal.connect(self.handle_error_selected)
            check_widget.run_signal.connect(self.handle_run)
            check_widget.fix_signal.connect(self.handle_fix)
            
        self.content_layout.addStretch()
        
        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout(button_widget)
        
        uncheck_button = QtWidgets.QPushButton("Uncheck")
        uncheck_button.clicked.connect(self.uncheck)
        
        invert_button = QtWidgets.QPushButton("Invert")
        invert_button.clicked.connect(self.invert_checks)
        
        uncheck_passed_button = QtWidgets.QPushButton("Uncheck Passed")
        uncheck_passed_button.clicked.connect(lambda: self.uncheck_passed_signal.emit())
        
        check_all_button = QtWidgets.QPushButton("Check All")
        check_all_button.clicked.connect(self.check_all)
        
        button_layout.addWidget(uncheck_button)
        button_layout.addWidget(invert_button)
        button_layout.addWidget(uncheck_passed_button)
        button_layout.addWidget(check_all_button)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(button_widget)


    def update_checks(self, settings):
        """Update the check widgets based on the selected preset set."""
        all_widgets = self.get_all_widgets(active=False)
        preset_set = settings['preset_set']
        disabled_checks_visible = settings['disabled_checks_visible']
        selected_severity = settings['severity'] 

        for check_widget in all_widgets:
            check_severity = check_widget.check.severity 
            status = check_severity >= selected_severity and check_widget.check.name in preset_set
            check_widget.set_status(status, disabled_checks_visible)

    def reset_checks(self):
        for check_widget in self.checks.values():
            check_widget.reset_ui()  
    
    def get_all_widgets(self, active: bool = False):
        sorted_checks = sorted(self.checks.values(), key=lambda widget: (widget.check.category, widget.check.label))
        check_widgets = []

        for check_widget in sorted_checks:
            if active:
                if check_widget.is_checked() and check_widget.isEnabled():
                    check_widgets.append(check_widget)
            else:
                check_widgets.append(check_widget)

        return check_widgets
    
    def uncheck_passed(self, error_object):
        for check_widget in self.checks.values():
            name = check_widget.check.name
            should_be_checked = name in error_object and len(error_object[name]) > 0
            check_widget.set_checked(should_be_checked)

    
    def invert_checks(self):
        for check_widget in self.checks.values():
            check_widget.set_checked(not check_widget.is_checked())
            
    def uncheck(self):
        for check_widget in self.checks.values():
            check_widget.set_checked(False)
            
    def check_all(self):
        for check_widget in self.checks.values():
            check_widget.set_checked(True)
            
    def handle_error_selected(self, check):
        self.select_error_signal.emit(check)
        
    def handle_fix(self, check):
        self.fix_signal.emit(check)
        
    def handle_run(self, check):
        self.run_signal.emit(check)
