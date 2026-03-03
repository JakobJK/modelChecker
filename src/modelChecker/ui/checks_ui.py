from PySide6 import QtWidgets, QtCore

from modelChecker.checks import all_checks

from modelChecker.ui.check_widget import CheckWidget
from modelChecker.ui.category_widget import CategoryWidget
from modelChecker.validation_check_base import ValidationCheckBase

class ChecksUI(QtWidgets.QGroupBox):
    select_error_signal = QtCore.Signal(object)
    run_signal = QtCore.Signal(object)
    fix_signal = QtCore.Signal(object)
    uncheck_passed_signal = QtCore.Signal()
    
    def __init__(self):
        super().__init__("Model Checks")
        
        self._categories = {}
        self._checks = {}

        self.build_ui()


    def build_ui(self): 
        main_layout = QtWidgets.QVBoxLayout(self)
        
        checks_layout = self._create_checks_layout() 
        buttons_layout = self._create_button_layout()

        main_layout.addWidget(checks_layout)
        main_layout.addWidget(buttons_layout)

    def _create_checks_layout(self):
        content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0) 

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setContentsMargins(0, 0, 0, 0)

        categories = sorted({x.category for x in all_checks})
        for category in categories:
            category_widget = CategoryWidget(category)
            self._categories[category] = category_widget
            self.content_layout.addWidget(category_widget)

        sorted_checks = sorted(all_checks, key=lambda x: x.label)
        for check in sorted_checks:
            check_widget = CheckWidget(check)
            self._checks[check.name] = check_widget
            self._categories[check.category].add_check(check_widget)
            check_widget.run_signal.connect(self.handle_run)
            check_widget.fix_signal.connect(self.handle_fix)
        return scroll_area



    def _create_button_layout(self):
        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        uncheck_button = QtWidgets.QPushButton("Uncheck") 
        invert_button = QtWidgets.QPushButton("Invert")
        uncheck_passed_button = QtWidgets.QPushButton("Uncheck Passed")
        check_all_button = QtWidgets.QPushButton("Check All")

        uncheck_button.clicked.connect(self.uncheck)
        invert_button.clicked.connect(self.invert_checks)
        uncheck_passed_button.clicked.connect(lambda: self.uncheck_passed_signal.emit())
        check_all_button.clicked.connect(self.check_all)
        
        button_layout.addWidget(uncheck_button)
        button_layout.addWidget(invert_button)
        button_layout.addWidget(uncheck_passed_button)
        button_layout.addWidget(check_all_button)
        
        return button_widget 
   
     
    @property
    def checks(self):
        sorted_checks = sorted(self._checks.values(), key=lambda widget: (widget.check.category, widget.check.label))
        checks = []
        for check_widget in sorted_checks:
            checks.append(check_widget.check)
        return checks
    
    @property
    def active_checks(self):
        sorted_checks = sorted(self._checks.values(), key=lambda widget: (widget.check.category, widget.check.label))
        checks = []
        for check_widget in sorted_checks:
            if check_widget.isEnabled():
                checks.append(check_widget.check)
        return checks
    
    def uncheck_passed(self, error_object):
        for check_widget in self._checks.values():
            name = check_widget.check.name
            should_be_checked = name in error_object and len(error_object[name]) > 0
            check_widget.set_checked(should_be_checked)

    def invert_checks(self):
        for check_widget in self._checks.values():
            check_widget.set_checked(not check_widget.is_checked())
            
    def uncheck(self):
        for check_widget in self._checks.values():
            check_widget.set_checked(False)
            
    def check_all(self):
        for check_widget in self._checks.values():
            check_widget.set_checked(True)
            
    def handle_error_selected(self, check):
        self.select_error_signal.emit(check)
        
    def handle_fix(self, check):
        self.fix_signal.emit(check)
        
    def handle_run(self, check):
        self.run_signal.emit(check)
