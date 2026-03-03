import maya.OpenMayaUI as omui
from PySide6 import QtCore, QtWidgets
from shiboken6 import wrapInstance
from modelChecker.constants import TITLE, OBJ_NAME 
from modelChecker.__version__ import __version__
from modelChecker.ui.report_ui import ReportUI
from modelChecker.ui.checks_ui import ChecksUI

def get_main_window():
    main_window_pointer = omui.MQtUtil.mainWindow()
    main_window = wrapInstance(int(main_window_pointer), QtWidgets.QWidget)
    return main_window

class UI(QtWidgets.QMainWindow):
    qmw_instance = None

    @classmethod
    def show_UI(cls):
        if not cls.qmw_instance:
            cls.qmw_instance = UI()
        if cls.qmw_instance.isHidden():
            cls.qmw_instance.show()
        else:
            cls.qmw_instance.raise_()
            cls.qmw_instance.activateWindow()
        return cls.qmw_instance 


    def __init__(self, parent=get_main_window()):
        super().__init__(parent=parent)
        self.setObjectName(OBJ_NAME)
        self.setWindowTitle(f"{TITLE} - {__version__}")
        self.connect_signals() 
        self.build_ui()
    
    def connect_signals(self):
        self.checks_ui = ChecksUI()
        self.checks_ui.fix_signal.connect(self.handle_fix)
        self.checks_ui.run_signal.connect(self.handle_run)
        self.checks_ui.uncheck_passed_signal.connect(self.handle_uncheck_passed)
        
    
    def build_ui(self):
        main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        splitter = QtWidgets.QSplitter()
        
        report_buttons_widget = QtWidgets.QWidget()
        report_buttons_layout = QtWidgets.QHBoxLayout(report_buttons_widget)
        report_buttons_layout.addStretch()
        
        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.clicked.connect(self.clear)
        
        report_buttons_layout.addWidget(clear_button)
        run_all_button = QtWidgets.QPushButton("Run Checks on Selected / All")
        run_all_button.clicked.connect(self.run_all)
        report_buttons_layout.addWidget(run_all_button)
        
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        
        left_layout.addWidget(self.checks_ui)
        
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        
        right_layout.addWidget(report_buttons_widget)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter)
    
        
    def handle_fix(self, check):
        """Handle the check selection and update the UI accordingly."""
        self.runner.fix(check)
        
    def handle_run(self, check):
        """Handle the check selection and update the UI accordingly."""
        self.runner.run([check], refresh_context=False)
    
    def run_all(self):
        self.checks_ui.reset_checks()
        active_checks_widgets = self.checks_ui.get_all_widgets(active=True)
        self.runner.run(active_checks_widgets)
        
    def handle_uncheck_passed(self):
        result_object = self.runner.get_result_object()
        if "error_object" in result_object:
            self.checks_ui.uncheck_passed(result_object['error_object'])
    
        
    def handle_run_result(self, result_object):
        all_widgets = self.checks_ui.get_all_widgets(active=False)
        
    def handle_verbose_level_change(self):
        result_object = self.runner.get_result_object()
        if "maya_error_object" in result_object or "usd_error_object" in result_object:
            all_widgets = self.checks_ui.get_all_widgets(active=False)
    
        
    def handle_settings_changed(self, settings):
        """Handle preset change and update the checks UI."""
        self.checks_ui.update_checks(settings)
    
    def clear(self):
        self.checks_ui.reset_checks()
