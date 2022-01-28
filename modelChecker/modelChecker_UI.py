"""
    modelChecker v.0.1.1
    Reliable production ready sanity checker for Autodesk Maya
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
        mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class UI(QtWidgets.QMainWindow):

    qmwInstance = None
    version = '0.1.1'
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

        selectedModelLabel = QtWidgets.QLabel("Top Node")
        selectedModelLabel.setMaximumWidth(60)

        self.selectedTopNode_UI = QtWidgets.QLineEdit("")
        self.selectedTopNode_UI.setMaximumWidth(200)

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
            if sys.version_info.major >= 3:
                text = '\u2193'
            else:
                text = u'\u2193'.encode('utf-8')
            self.categoryCollapse[obj] = QtWidgets.QPushButton(text)
            self.categoryCollapse[obj].clicked.connect(
                partial(self.toggleUI, obj))
            self.categoryCollapse[obj].setMaximumWidth(30)
            self.categoryButton[obj].setStyleSheet(
                "background-color: grey; text-transform: uppercase; color: #000000; font-size: 18px;")
            self.categoryButton[obj].clicked.connect(
                partial(self.checkCategory, obj))
            self.categoryHeader[obj].addWidget(self.categoryButton[obj])
            self.categoryHeader[obj].addWidget(self.categoryCollapse[obj])
            self.categoryWidget[obj].setLayout(self.categoryLayout[obj])
            checks.addLayout(self.categoryHeader[obj])
            checks.addWidget(self.categoryWidget[obj])

        # Creates the buttons with their settings
        for obj in self.commandsList:
            name = obj['func']
            label = obj['label']
            category = obj['category']
            check = obj['defaultChecked']

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
            self.commandLabel[name].setMinimumWidth(120)
            self.commandLabel[name].setStyleSheet("padding: 2px;")
            self.commandCheckBox[name] = QtWidgets.QCheckBox()

            self.commandCheckBox[name].setChecked(check)
            self.commandCheckBox[name].setMaximumWidth(20)

            self.commandRunButton[name] = QtWidgets.QPushButton("Run")
            self.commandRunButton[name].setMaximumWidth(30)

            self.commandRunButton[name].clicked.connect(
                partial(self.commandToRun, [obj]))

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

    def getCategories(self, incomingList):
        allCategories = []
        for obj in incomingList:
            allCategories.append(obj['category'])
        return set(allCategories)

    def setTopNode(self):
        sel = cmds.ls(selection=True)
        self.selectedTopNode_UI.setText(sel[0])

    def checkState(self, name):
        return self.commandCheckBox[name].checkState()

    def checkAll(self):
        for obj in self.commandsList:
            name = obj['func']
            self.commandCheckBox[obj['func']].setChecked(True)

    def getArrow(self):
        pass

    def toggleUI(self, obj):
        state = self.categoryWidget[obj].isVisible()
        if state:
            if sys.version_info.major >= 3:
                text = u'\u21B5'
            else:
                text = u'\u21B5'.encode('utf-8')
            self.categoryCollapse[obj].setText(text)
            self.categoryWidget[obj].setVisible(not state)
            self.adjustSize()
        else:
            if sys.version_info.major >= 3:
                text = u'\u2193'
            else:
                text = u'\u2193'.encode('utf-8')
            self.categoryCollapse[obj].setText(text)
            self.categoryWidget[obj].setVisible(not state)

    def uncheckAll(self):
        for obj in self.commandsList:
            name = obj['func']
            self.commandCheckBox[name].setChecked(False)

    def invertCheck(self):
        for obj in self.commandsList:
            name = obj['func']
            self.commandCheckBox[name].setChecked(
                not self.commandCheckBox[name].isChecked())

    def checkCategory(self, category):

        uncheckedCategoryButtons = []
        categoryButtons = []

        for obj in self.commandsList:
            name = obj['func']
            cat = obj['category']
            if cat == category:
                categoryButtons.append(name)
                if self.commandCheckBox[name].isChecked():
                    uncheckedCategoryButtons.append(name)

        for obj in categoryButtons:
            if len(uncheckedCategoryButtons) == len(categoryButtons):
                self.commandCheckBox[obj].setChecked(False)
            else:
                self.commandCheckBox[obj].setChecked(True)

    # Filter Nodes
    def filterNodes(self):
        nodes = []
        self.SLMesh.clear()
        allUsuableNodes = []
        allNodes = cmds.ls(transforms=True)
        for obj in allNodes:
            if not obj in {'front', 'persp', 'top', 'side'}:
                allUsuableNodes.append(obj)

        selection = cmds.ls(sl=True)
        topNode = self.selectedTopNode_UI.text()
        if len(selection) > 0:
            nodes = selection
        elif self.selectedTopNode_UI.text() == "":
            nodes = allUsuableNodes
        else:
            if cmds.objExists(topNode):
                nodes = cmds.listRelatives(
                    topNode, allDescendents=True, typ="transform")
                if not nodes:
                    nodes = topNode
                nodes.append(topNode)
            else:
                response = "Object in Top Node doesn't exists\n"
                self.reportOutputUI.clear()
                self.reportOutputUI.insertPlainText(response)
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, typ="mesh")
            if shapes:
                self.SLMesh.add(node)
        return nodes

    def commandToRun(self, commands):
        nodes = self.filterNodes()
        self.reportOutputUI.clear()
        if len(nodes) == 0:
            self.reportOutputUI.insertPlainText("Error - No nodes to check\n")
        else:
            for currentCommand in commands:
                command = currentCommand['func']
                label = currentCommand['label']
                self.errorNodes = getattr(
                    mcc, command)(nodes, self.SLMesh)
                if self.errorNodes:
                    self.reportOutputUI.insertHtml(
                        label + " -- <font color='#996666'>FAILED</font><br>")
                    for obj in self.errorNodes:
                        self.reportOutputUI.insertPlainText(
                            "    " + obj + "\n")

                    self.errorNodesButton[command].setEnabled(True)
                    self.errorNodesButton[command].clicked.connect(
                        partial(self.selectErrorNodes, self.errorNodes))
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
        for obj in self.commandsList:
            name = obj['func']
            if self.commandCheckBox[name].isChecked():
                checkedCommands.append(obj)
            else:
                self.commandLabel[name].setStyleSheet(
                    "background-color: none; padding: 2px;")
                self.errorNodesButton[name].setEnabled(False)
        if len(checkedCommands) == 0:
            print("You have to select something")
        else:
            self.commandToRun(checkedCommands)

    def selectErrorNodes(self, list):
        cmds.select(list)


if __name__ == '__main__':
    try:
        win.close()
    except:
        pass
    win = UI(parent=getMainWindow())
    win.show()
    win.raise_()
