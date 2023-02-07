"""
    modelChecker v.0.1.2
    Model sanity checker for Autodesk Maya
    Contact: jakobjk@gmail.com
    https://github.com/JakobJK/modelChecker
"""

from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
from functools import partial

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import modelChecker.modelChecker_commands as mcc
import modelChecker.modelChecker_list as mcl
import sys


def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        mainWindow = wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        # Support for Maya 2016
        mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class UI(QtWidgets.QMainWindow):

    qmwInstance = None
    version = '0.1.2'
    SLMesh = om.MSelectionList()
    commandsList = mcl.mcCommandsList
    reportOutputUI = QtWidgets.QTextEdit()
    categoryLayout = {}
    categoryWidget = {}
    categoryButton = {}
    categoryHeader = {}
    categoryCollapse = {}
    command = {}
    commandWidget = {}
    commandLayout = {}
    commandLabel = {}
    commandCheckBox = {}
    errorNodesButton = {}
    commandRunButton = {}

    @classmethod
    def show_UI(cls):
        if not cls.qmwInstance:
            cls.qmwInstance = UI()
        if cls.qmwInstance.isHidden():
            cls.qmwInstance.show()
        else:
            cls.qmwInstance.raise_()
            cls.qmwInstance.activateWindow()

    def __init__(self, parent=getMainWindow()):
        super(UI, self).__init__(
            parent, QtCore.Qt.WindowStaysOnTopHint)

        self.setObjectName("ModelCheckerUI")
        self.setWindowTitle('Model Checker' + ' ' + self.version)

        mainLayout = QtWidgets.QWidget(self)
        self.setCentralWidget(mainLayout)

        columns = QtWidgets.QHBoxLayout(mainLayout)
        report = QtWidgets.QVBoxLayout()
        checks = QtWidgets.QVBoxLayout()

        columns.addLayout(checks)
        columns.addLayout(report)

        selectedModelVLayout = QtWidgets.QHBoxLayout()
        checks.addLayout(selectedModelVLayout)

        selectedModelLabel = QtWidgets.QLabel("Root Node")
        selectedModelLabel.setMaximumWidth(80)

        self.selectedTopNode_UI = QtWidgets.QLineEdit("")
        # self.selectedTopNode_UI.setMaximumWidth()

        selectedModelNodeButton = QtWidgets.QPushButton("Select")
        selectedModelNodeButton.setMaximumWidth(60)
        selectedModelNodeButton.clicked.connect(self.setTopNode)

        selectedModelVLayout.addWidget(selectedModelLabel)
        selectedModelVLayout.addWidget(self.selectedTopNode_UI)
        selectedModelVLayout.addWidget(selectedModelNodeButton)

        reportBoxLayout = QtWidgets.QHBoxLayout()
        reportLabel = QtWidgets.QLabel("Report:")

        reportBoxLayout.addWidget(reportLabel)
        report.addLayout(reportBoxLayout)

        self.reportOutputUI.setMinimumWidth(600)
        report.addWidget(self.reportOutputUI)

        self.checkRunButton = QtWidgets.QPushButton("Run All Checked")
        self.checkRunButton.clicked.connect(self.sanityCheck)

        report.addWidget(self.checkRunButton)

        clearButton = QtWidgets.QPushButton("Clear")
        clearButton.setMaximumWidth(150)
        clearButton.clicked.connect(partial(self.reportOutputUI.clear))
        reportBoxLayout.addWidget(clearButton)
        self.resize(1000, 900)
        category = self.getCategories(self.commandsList)

        for obj in category:
            self.categoryWidget[obj] = QtWidgets.QWidget()
            self.categoryLayout[obj] = QtWidgets.QVBoxLayout()
            self.categoryHeader[obj] = QtWidgets.QHBoxLayout()
            self.categoryButton[obj] = QtWidgets.QPushButton(obj)
            text = '\u2193' if sys.version_info.major >= 3 else u'\u2193'.encode('utf-8')
            self.categoryCollapse[obj] = QtWidgets.QPushButton(text)
            self.categoryCollapse[obj].clicked.connect(
                partial(self.toggleUI, obj))
            self.categoryCollapse[obj].setMaximumWidth(30)
            self.categoryButton[obj].setStyleSheet(
                """background-color: grey; 
                text-transform: uppercase; 
                color: #000000; font-size: 
                18px;""")
            self.categoryButton[obj].clicked.connect(
                partial(self.checkCategory, obj))
            self.categoryHeader[obj].addWidget(self.categoryButton[obj])
            self.categoryHeader[obj].addWidget(self.categoryCollapse[obj])
            self.categoryWidget[obj].setLayout(self.categoryLayout[obj])
            checks.addLayout(self.categoryHeader[obj])
            checks.addWidget(self.categoryWidget[obj])

        # Creates the buttons with their settings
        for command in self.commandsList:
            name = command['func']
            label = command['label']
            category = command['category']
            check = command['defaultChecked']

            self.commandWidget[name] = QtWidgets.QWidget()
            self.commandWidget[name].setMaximumHeight(40)
            self.commandLayout[name] = QtWidgets.QHBoxLayout()

            self.categoryLayout[category].addWidget(self.commandWidget[name])
            self.commandWidget[name].setLayout(self.commandLayout[name])

            self.commandLayout[name].setSpacing(4)
            self.commandLayout[name].setContentsMargins(0, 0, 0, 0)
            self.commandWidget[name].setStyleSheet(
                "padding: 0px; margin: 0px;")
            self.command[name] = name
            self.commandLabel[name] = QtWidgets.QLabel(label)
            self.commandLabel[name].setMinimumWidth(180)
            self.commandLabel[name].setStyleSheet("padding: 2px;")
            self.commandCheckBox[name] = QtWidgets.QCheckBox()

            self.commandCheckBox[name].setChecked(check)
            self.commandCheckBox[name].setMaximumWidth(20)

            self.commandRunButton[name] = QtWidgets.QPushButton("Run")
            self.commandRunButton[name].setMaximumWidth(40)

            self.commandRunButton[name].clicked.connect(
                partial(self.commandToRun, [command]))

            self.errorNodesButton[name] = QtWidgets.QPushButton(
                "Select Error Nodes")
            self.errorNodesButton[name].setEnabled(False)
            self.errorNodesButton[name].setMaximumWidth(150)

            self.commandLayout[name].addWidget(self.commandLabel[name])
            self.commandLayout[name].addWidget(self.commandCheckBox[name])
            self.commandLayout[name].addWidget(self.commandRunButton[name])
            self.commandLayout[name].addWidget(self.errorNodesButton[name])

        checks.addStretch()

        checkButtonsLayout = QtWidgets.QHBoxLayout()
        checks.addLayout(checkButtonsLayout)

        uncheckAllButton = QtWidgets.QPushButton("Uncheck All")
        uncheckAllButton.clicked.connect(self.uncheckAll)

        invertCheckButton = QtWidgets.QPushButton("Invert")
        invertCheckButton.clicked.connect(self.invertCheck)

        checkAllButton = QtWidgets.QPushButton("Check All")
        checkAllButton.clicked.connect(self.checkAll)

        checkButtonsLayout.addWidget(uncheckAllButton)
        checkButtonsLayout.addWidget(invertCheckButton)
        checkButtonsLayout.addWidget(checkAllButton)

    def getCategories(self, commands):
        allCategories = set()
        for command in commands:
            allCategories.add(command['category'])
        return allCategories

    def setTopNode(self):
        sel = cmds.ls(selection=True)
        self.selectedTopNode_UI.setText(sel[0])

    def checkState(self, name):
        return self.commandCheckBox[name].checkState()

    def checkAll(self):
        for command in self.commandsList:
            self.commandCheckBox[command['func']].setChecked(True)

    def toggleUI(self, category):
        state = self.categoryWidget[category].isVisible()
        buttonLabel = u'\u21B5' if state else u'\u2193'
        text = buttonLabel if sys.version_info.major >= 3 else buttonLabel.encode('utf-8')
        self.adjustSize()
        self.categoryCollapse[category].setText(text)
        self.categoryWidget[category].setVisible(not state)

    def uncheckAll(self):
        for command in self.commandsList:
            name = command['func']
            self.commandCheckBox[name].setChecked(False)

    def invertCheck(self):
        for command in self.commandsList:
            name = command['func']
            self.commandCheckBox[name].setChecked(
                not self.commandCheckBox[name].isChecked())

    def checkCategory(self, category):
        uncheckedCategoryButtons = []
        categoryButtons = []

        for command in self.commandsList:
            name = command['func']
            cat = command['category']
            if cat == category:
                categoryButtons.append(name)
                if self.commandCheckBox[name].isChecked():
                    uncheckedCategoryButtons.append(name)

        for category in categoryButtons:
            checked = len(uncheckedCategoryButtons) != len(categoryButtons)
            self.commandCheckBox[category].setChecked(checked)

    def filterNodes(self):
        self.SLMesh.clear()
        selection = cmds.ls(selection=True, typ="transform")
        if len(selection) > 0:
            nodes = selection
        elif self.selectedTopNode_UI.text() == "":
            nodes = self.filterGetAllNodes()
        else:
            topNode = self.selectedTopNode_UI.text()
            nodes = self.filterGetTopNode(topNode)
            if not nodes:
                self.reportOutputUI.clear()
                self.reportOutputUI.insertPlainText("Object in Root Node doesn't exists\n")
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, typ="mesh")
            if shapes:
                self.SLMesh.add(node)
        return nodes

    def filterGetTopNode(self, topNode):
        nodes = []
        if cmds.objExists(topNode):
            nodes = cmds.listRelatives(
                topNode, allDescendents=True, typ="transform")
            nodes.append(topNode)
        return nodes

    def filterGetAllNodes(self):
        allNodes = cmds.ls(transforms=True)
        allUsuableNodes = []
        for node in allNodes:
            if not node in {'front', 'persp', 'top', 'side'}:
                allUsuableNodes.append(node)
        return allUsuableNodes


    def commandToRun(self, commands):
        nodes = self.filterNodes()
        self.reportOutputUI.clear()
        if len(nodes) == 0:
            self.reportOutputUI.insertPlainText("Error - No nodes to check\n")
        else:
            for currentCommand in commands:
                command = currentCommand['func']
                label = currentCommand['label']
                error = getattr(
                    mcc, command)(nodes, self.SLMesh)
                if error:
                    self.reportOutputUI.insertHtml(
                        label + " -- <font color='#996666'>FAILED</font><br>")
                    for obj in error:
                        self.reportOutputUI.insertPlainText(
                            "    " + obj + "\n")
                    self.errorNodesButton[command].setEnabled(True)
                    self.errorNodesButton[command].clicked.connect(
                        partial(self.selectErrorNodes, error))
                    self.commandLabel[command].setStyleSheet(
                        "background-color: #664444; padding: 2px;")
                else:
                    self.commandLabel[command].setStyleSheet(
                        "background-color: #446644; padding: 2px;")
                    self.reportOutputUI.insertHtml(
                        label + " -- <font color='#669966'>SUCCESS</font><br>")
                    self.errorNodesButton[command].setEnabled(False)

    def sanityCheck(self):
        self.reportOutputUI.clear()
        checkedCommands = []
        for command in self.commandsList:
            name = command['func']
            if self.commandCheckBox[name].isChecked():
                checkedCommands.append(command)
            else:
                self.commandLabel[name].setStyleSheet(
                    "background-color: none; padding: 2px;")
                self.errorNodesButton[name].setEnabled(False)
        if checkedCommands:
            self.commandToRun(checkedCommands)

    def selectErrorNodes(self, nodes):
        cmds.select(nodes)

if __name__ == '__main__':
    try:
        win.close()
    except:
        pass
    win = UI(parent=getMainWindow())
    win.show()
    win.raise_()
    