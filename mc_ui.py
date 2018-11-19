# model checker UI

from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui


def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow

class modelChecker(QtWidgets.QMainWindow):
    def __init__(self, parent=getMainWindow()):
        super(modelChecker, self).__init__(parent)
        
        ##Creates object, Title Name and Adds a QtWidget as our central widget/Main Layout
        self.setObjectName("modelCheckerUI")
        self.setWindowTitle("Model Checker")
        mainLayout = QtWidgets.QWidget(self)
        self.setCentralWidget(mainLayout)
        
        ## Adding a Horizontal layout to divide the UI in two columns
        columns = QtWidgets.QHBoxLayout(mainLayout)
        
        
        ##Creating 2 vertical layout for the sanity checks and one for the report
        
        self.report = QtWidgets.QVBoxLayout()
        self.checks = QtWidgets.QVBoxLayout()
        

        
        columns.addLayout(self.checks)
        columns.addLayout(self.report)
        
        ##### Adding UI ELEMENTS FOR CHECKS
        
        
        selectedModelVLayout = QtWidgets.QHBoxLayout()
        self.checks.addLayout(selectedModelVLayout)

        
        selectedModelLabel = QtWidgets.QLabel("Select Top Model Node")
        selectedModelLabel.setMaximumWidth(60)
        
        self.selectedTopNode_UI = QtWidgets.QLineEdit("model_grp ")
        self.selectedTopNode_UI.setMaximumWidth(200)
        
        self.selectedModelNodeButton = QtWidgets.QPushButton("Select")
        self.selectedModelNodeButton.setMaximumWidth(100)
        
        
        
        selectedModelVLayout.addWidget(selectedModelLabel)
        selectedModelVLayout.addWidget(self.selectedTopNode_UI)
        selectedModelVLayout.addWidget(self.selectedModelNodeButton)
        
        
        
        ## ADDING UI ELEMENTS FOR REPPORT
        
        reportLabel = QtWidgets.QLabel("Report:")
       
        self.report.addWidget(reportLabel)
        
        
        self.reportOutputUI = QtWidgets.QPlainTextEdit()
        self.report.addWidget(self.reportOutputUI)
        
        self.checkRunButton = QtWidgets.QPushButton("Run Sanity Check")
        self.report.addWidget(self.checkRunButton)
        
        
        
        # Adding the stretch element to the checks UI to get everything at the top
        self.resize(1000,900)
        
    def addMenuItem(self, cnName, cnCategory, cnCheck, fix):

        checkBox = cnName + "CheckBox"
        layout = cnName + "Layout"
        nameLabel = cnName + "label"
        
        categoryTitle = QtWidgets.QLabel(cnCategory)
        categoryTitle.setStyleSheet("background-color: lightgreen; color: #000000; font-size: 22px;")
        self.checks.addWidget(categoryTitle)
        nameSpacesLayout = QtWidgets.QHBoxLayout()
        self.checks.addLayout(nameSpacesLayout)
        nameSpaceLabel = QtWidgets.QLabel(cnName)
        nameSpaceLabel.setMinimumWidth(150)
        nameSpacesLayout.addWidget(nameSpaceLabel)
        nameSpaceCheckBox = QtWidgets.QCheckBox()
        nameSpaceCheckBox.setChecked(cnCheck)
        nameSpacesLayout.addWidget(nameSpaceCheckBox)
        nameSpaceErrorNodes = QtWidgets.QPushButton("Select Error Nodes")
        nameSpacesLayout.addWidget(nameSpaceErrorNodes)
        nameSpaceFix = QtWidgets.QPushButton("Fix")
        nameSpaceFix.setMaximumWidth(40)
        nameSpacesLayout.addWidget(nameSpaceFix)
        
    def addStretch(self):
        self.checks.addStretch()
        
    def printThis(this):
        print this
    

def show():
    win = modelChecker(parent=getMainWindow())
    win.addMenuItem('history','General', 1, 1)
    win.addMenuItem('duplicatedNames','Naming', 1, 0)
    win.addMenuItem('noneQuads','Topology', 1, 1)
    win.addMenuItem('Overlapping UV Shells','UVs', 0, 0)
    win.addStretch()
    win.show()
    win.raise_()
    return win
    
    
show()