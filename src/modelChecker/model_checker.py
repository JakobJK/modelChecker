import maya.OpenMayaUI as omui
from PySide6 import QtCore, QtWidgets
from shiboken6 import wrapInstance
from modelChecker.constants import TITLE, OBJ_NAME 
from modelChecker.__version__ import __version__
from modelChecker.ui.report_ui import ReportUI
from modelChecker.ui.checks_ui import ChecksUI
from modelChecker.ui.settings_ui import SettingsUI
from modelChecker.ui.progress_ui import ProgressUI
from modelChecker.runner import Runner

def get_main_window():
    main_window_pointer = omui.MQtUtil.mainWindow()
    main_window = wrapInstance(int(main_window_pointer), QtWidgets.QWidget)
    return main_window        

class UI(QtWidgets.QMainWindow):
    qmwInstance = None
    
    @classmethod
    def show_UI(cls):
        if not cls.qmwInstance:
            cls.qmwInstance = UI()
        if cls.qmwInstance.isHidden():
            cls.qmwInstance.show()
        else:
            cls.qmwInstance.raise_()
            cls.qmwInstance.activateWindow()

    def __init__(self, parent=get_main_window()):
        super().__init__()
        
        self.current_check = None
        
        self.setObjectName(OBJ_NAME)
        self.setWindowTitle(f"{TITLE} - {__version__}")
        self.extend_ui_classes() 
        self.build_ui()
    
    def extend_ui_classes(self):
        self.checks_ui = ChecksUI()
        self.checks_ui.select_error_signal.connect(self.handle_error_selected)
        self.checks_ui.fix_signal.connect(self.handle_fix)
        self.checks_ui.run_signal.connect(self.handle_run)
        self.checks_ui.uncheck_passed_signal.connect(self.handle_uncheck_passed)
        
        self.report_ui = ReportUI()
        self.report_ui.verbosity_signal.connect(self.handle_verbose_level_change)
        
        self.progress_ui = ProgressUI()
        self.settings_ui = SettingsUI()
        self.settings_ui.on_settings_changed.connect(self.handle_settings_changed)
        
        self.runner = Runner()
        self.runner.result_signal.connect(self.handle_run_result)
        self.runner.progress_signal.connect(self.handle_progress)
        self.runner.error_signal.connect(self.handle_error_signal)
    
    def build_ui(self):
        main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)
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
        
        left_layout.addWidget(self.settings_ui)
        left_layout.addWidget(self.checks_ui)
        
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        
        right_layout.addWidget(self.progress_ui)
        right_layout.addWidget(self.report_ui)
        right_layout.addWidget(report_buttons_widget)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.runner.stop() 
        else:
            super().keyPressEvent(event)
    
    def handle_error_selected(self, checkwidget):
        """Handle the check selection and update the UI accordingly."""
        result_object = self.runner.get_result_object()
        
        maya_object = result_object.get('maya_error_object', {})
        usd_object = result_object.get('usd_error_object', {})
        
        checkwidget.check.do_select_error_nodes(maya_object, usd_object)
        
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
    
    def handle_progress(self, data):
        self.progress_ui.update(data)
        
    def handle_run_result(self, result_object):
        all_widgets = self.checks_ui.get_all_widgets(active=False)
        self.report_ui.render_report(result_object, all_widgets)
        
    def handle_verbose_level_change(self):
        result_object = self.runner.get_result_object()
        if "maya_error_object" in result_object or "usd_error_object" in result_object:
            all_widgets = self.checks_ui.get_all_widgets(active=False)
            self.report_ui.render_report(result_object, all_widgets)
    
    def handle_error_signal(self, data):
        self.report_ui.set_error(data['error'])
        
    def handle_settings_changed(self, settings):
        """Handle preset change and update the checks UI."""
        self.checks_ui.update_checks(settings)
    
    def clear(self):
        self.runner.reset_contexts()
        self.checks_ui.reset_checks()
        self.report_ui.clear()
        self.progress_ui.reset()
