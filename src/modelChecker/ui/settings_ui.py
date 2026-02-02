from PySide6 import QtWidgets, QtCore
from modelChecker.constants import Severity
from modelChecker.presets import all_presets

class SettingsUI(QtWidgets.QWidget):
    on_settings_changed = QtCore.Signal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.settings_expanded = False
        
        self._build_preset_ui()
        
        settings_layout = QtWidgets.QVBoxLayout(self)
        
        self.settings_widget = QtWidgets.QWidget()
        self.settings_widget.setVisible(self.settings_expanded)
        expanded_settings_layout = QtWidgets.QVBoxLayout(self.settings_widget)
        
        settings_group_box = QtWidgets.QGroupBox("Settings")
        group_box_layout = QtWidgets.QVBoxLayout(settings_group_box)
        
        
        self.severity_combo_box = QtWidgets.QComboBox(self)
        self.severity_combo_box.addItems([severity.name.capitalize() for severity in Severity])
        
        severity_widget = QtWidgets.QWidget()
        severity_layout = QtWidgets.QHBoxLayout(severity_widget)
        severity_layout.addWidget(QtWidgets.QLabel("Ignore below: "))
        severity_layout.addWidget(self.severity_combo_box, 1)
        
        
        self.disabled_checks_checkbox = QtWidgets.QCheckBox("Show Disabled Checks")
        
        expanded_settings_layout.addWidget(settings_group_box)
        
        group_box_layout.addWidget(severity_widget)
        group_box_layout.addWidget(self.disabled_checks_checkbox)
        
        settings_layout.addWidget(self.preset_widget)
        settings_layout.addWidget(self.settings_widget)
        
        self.setLayout(settings_layout)
        self.combo_box.currentIndexChanged.connect(self.on_preset_changed)
        self.disabled_checks_checkbox.toggled.connect(self.emit_settings_changed)
        self.severity_combo_box.currentIndexChanged.connect(self.emit_settings_changed)
    
    def _build_preset_ui(self):
        self.preset_widget = QtWidgets.QWidget()
        
        preset_layout = QtWidgets.QHBoxLayout(self.preset_widget)

        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.addItems([preset for preset, _ in all_presets])

        settings_button = QtWidgets.QPushButton("\u2699")
        settings_button.setMaximumWidth(30)
        settings_button.clicked.connect(self.toggle_settings)
        
        preset_layout.addWidget(QtWidgets.QLabel("Preset: "))
        preset_layout.addWidget(self.combo_box, 1)
        preset_layout.addWidget(settings_button)
    
    def on_preset_changed(self, index):
        self.emit_settings_changed()
        
    def toggle_settings(self):
        self.settings_expanded = not self.settings_expanded
        self.settings_widget.setVisible(self.settings_expanded)
    
    
    def emit_settings_changed(self):
        index = self.combo_box.currentIndex()
        preset, preset_set = all_presets[index]
        selected_severity = Severity[self.severity_combo_box.currentText().upper()]
        
        settings = {
            "preset_set": preset_set,
            "disabled_checks_visible": self.disabled_checks_checkbox.isChecked(),
            "severity": selected_severity,
        }
        
        # Emit the settings change signal
        self.on_settings_changed.emit(settings)
