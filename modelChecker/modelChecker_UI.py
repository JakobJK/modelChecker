from PySide2 import QtWidgets, QtGui, QtCore
from shiboken2 import wrapInstance
from functools import partial
import json
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import modelChecker.modelChecker_commands as mcc
import modelChecker.modelChecker_list as mcl

def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class UI(QtWidgets.QMainWindow):
    qmwInstance = None
    version = '0.1.3'
    commandsList = mcl.mcCommandsList
    categoryLayout = {}
    categoryWidget = {}
    categoryButton = {}
    categoryHeader = {}
    categoryCollapse = {}
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
        super(UI, self).__init__(parent)

        self.setObjectName("ModelCheckerUI")
        self.setWindowTitle(f"Model Checker {self.version}")
        self.diagnostics = {}
        self.currentContext = None
        self.contexts = {}
        self.contextRowItems = {}

        mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(mainWidget)
        mainLayout = QtWidgets.QVBoxLayout(mainWidget)  
        report = self.buildContextUI()
        checks = self.buildChecksList()
        left = QtWidgets.QWidget()
        right = QtWidgets.QWidget()
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(right)
        left.setLayout(checks)
        right.setLayout(report)
        mainLayout.addWidget(splitter)

        self.resize(1000, 900)

        self.loadSettings()
        
        self.consolidatedCheck.stateChanged.connect(self.createReport)

    def contextPopupMenu(self, position):
        contextMenu = QtWidgets.QMenu(self)

        checkSelectedContexts = QtWidgets.QAction("Check Selected Contexts", contextMenu)
        uncheckSelectedContexts = QtWidgets.QAction("Uncheck Selected Contexts", contextMenu)
        runChecksOnSelectedContexts = QtWidgets.QAction("Run Checks on Selected Contexts", contextMenu)
        addSelectedNodesAsNewContexts = QtWidgets.QAction("Add Selected Nodes as New Contexts", contextMenu)
        removeSelectedContexts = QtWidgets.QAction("Remove Selected Contexts", contextMenu)

        checkSelectedContexts.triggered.connect(self.checkSelected)
        uncheckSelectedContexts.triggered.connect(self.uncheckSelected)
        runChecksOnSelectedContexts.triggered.connect(self.runChecksOnSelectedContexts)
        addSelectedNodesAsNewContexts.triggered.connect(self.addSelectedNodesAsNewContexts)
        removeSelectedContexts.triggered.connect(self.removeSelectedContexts)

        contextMenu.addAction(checkSelectedContexts)
        contextMenu.addAction(uncheckSelectedContexts)
        contextMenu.addSeparator()
        contextMenu.addAction(runChecksOnSelectedContexts)
        contextMenu.addSeparator()
        contextMenu.addAction(addSelectedNodesAsNewContexts)
        contextMenu.addAction(removeSelectedContexts)
        contextMenu.exec_(self.contextTable.viewport().mapToGlobal(position))
    

    def checkSelected(self):
        indexes = self.contextTable.selectionModel().selectedRows()
        for index in indexes:
            rowIdx = index.row()
            if rowIdx > 1:
                contextItem = self.contextTable.item(rowIdx, 0)
                contextItem.setCheckState(QtCore.Qt.Checked)
    
    def uncheckSelected(self):
        indexes = self.contextTable.selectionModel().selectedRows()
        for index in indexes:
            rowIdx = index.row()
            if rowIdx > 1:
                contextItem = self.contextTable.item(rowIdx, 0)
                contextItem.setCheckState(QtCore.Qt.Unchecked)

    def runChecksOnSelectedContexts(self):
        for index in range(self.contextTable.rowCount()):
            contextItem = self.contextTable.item(index, 0)
            if contextItem.checkState() == QtCore.Qt.Checked:
                print("You selected: Item", index)
    
    def addSelectedNodesAsNewContexts(self):
        selectedNodes = cmds.ls(selection=True)
        for node in selectedNodes:
            self.contextRowItems[node] = QtWidgets.QTableWidgetItem(node)
            contextItem = self.contextRowItems[node]
            contextItem.setFlags(contextItem.flags() | QtCore.Qt.ItemIsUserCheckable)
            contextItem.setCheckState(QtCore.Qt.Checked)
            newRowIdx = self.contextTable.rowCount()
            self.contextTable.insertRow(newRowIdx)
            self.contextTable.setItem(newRowIdx, 0, contextItem)
    


    def checkForParent(self, node):

        current_node = node
        while current_node:
            if current_node := cmds.listRelatives(node, parent=True):
                uuid = cmds.ls(current_node[0], uuid=True)[0]
                if uuid in self.contexts:
                    return current_node[0]

            


    def removeSelectedContexts(self):
        idxs = self.contextTable.selectionModel().selectedRows()
        for idx in sorted(idxs, reverse=True):
            self.contextTable.removeRow(idx.row())

    def onItemClicked(self, item):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.NoModifier:
            print("You clicked: ", item.text())


    def buildContextUI(self):
        """" Code for building the context UI"""
        report = QtWidgets.QVBoxLayout()
        self.contextTable = QtWidgets.QTableWidget()

        self.contextTable.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.contextTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # Configure the table        
        # 
        defaultContexts = ["Selection", "Global"]
        contextHeaders = ['CONTEXT', 'TESTS']
        self.contextTable.setColumnCount(len(contextHeaders))
        self.contextTable.setHorizontalHeaderLabels(contextHeaders)
        self.contextTable.verticalHeader().setVisible(False)
        self.contextTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.contextTable.setColumnWidth(0, 10)
        self.contextTable.setColumnWidth(2, 10)

        # Create context menu for the table
        self.contextTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.contextTable.itemClicked.connect(self.onItemClicked)
        self.contextTable.customContextMenuRequested.connect(self.contextPopupMenu)


        for idx, context in enumerate(defaultContexts):
            self.contextRowItems[context] = QtWidgets.QTableWidgetItem(context)
            contextItem = self.contextRowItems[context]
            contextItem.setFlags(contextItem.flags() & ~QtCore.Qt.ItemIsEditable)

            # if the contect is selection, let's make the contextItem uncheckable
            if context == "Selection" or context == "Global":
                contextItem.setFlags(contextItem.flags() & ~QtCore.Qt.ItemIsUserCheckable)
            else:
                contextItem.setFlags(contextItem.flags() | QtCore.Qt.ItemIsUserCheckable)
                
            if context == "Selection":
                contextItem.setCheckState(QtCore.Qt.Unchecked)
            else:
                contextItem.setCheckState(QtCore.Qt.Checked)
            self.contextTable.insertRow(idx)
            self.contextTable.setItem(idx, 0, contextItem)

        self.reportOutputUI = QtWidgets.QTextEdit()
        self.reportOutputUI.setReadOnly(True)
        self.reportOutputUI.setMinimumWidth(600)

        self.checkRunButton = QtWidgets.QPushButton("Run All Checked")
        self.consolidatedCheck = QtWidgets.QCheckBox()

        clearButton = QtWidgets.QPushButton("Clear")
        clearButton.setMaximumWidth(150)
        
        settingsLayout = QtWidgets.QHBoxLayout()
        settingsLayout.addWidget(QtWidgets.QLabel("Consolidated display: "))
        settingsLayout.addWidget(self.consolidatedCheck)
        
        runLayout = QtWidgets.QHBoxLayout()
        runLayout.addWidget(QtWidgets.QLabel("Report: "))
        runLayout.addWidget(clearButton)
        runLayout.addWidget(self.checkRunButton)

        
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)    
        splitter.addWidget(self.contextTable)
        splitter.addWidget(self.reportOutputUI)
        splitter.setSizes([200, 800])
        report.addLayout(settingsLayout)
        report.addWidget(splitter)
        report.addLayout(runLayout)

        self.checkRunButton.clicked.connect(self.sanityCheck)
        clearButton.clicked.connect(self.clearReport)
        
        return report

    def buildChecksList(self):
        """" Code for building the checks list UI"""
        checks = QtWidgets.QVBoxLayout()
        category = self.getCategories(self.commandsList)
        
        for obj in category:
            self.categoryWidget[obj] = QtWidgets.QWidget()
            self.categoryLayout[obj] = QtWidgets.QVBoxLayout()
            self.categoryHeader[obj] = QtWidgets.QHBoxLayout()
            self.categoryButton[obj] = QtWidgets.QPushButton(obj)
            self.categoryCollapse[obj] = QtWidgets.QPushButton('\u2193')
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

        for name in sorted(self.commandsList.keys()):
            label = self.commandsList[name]['label']
            category = self.commandsList[name]['category']

            self.commandWidget[name] = QtWidgets.QWidget()
            self.commandWidget[name].setMaximumHeight(40)
            self.commandLayout[name] = QtWidgets.QHBoxLayout()

            self.categoryLayout[category].addWidget(self.commandWidget[name])
            self.commandWidget[name].setLayout(self.commandLayout[name])

            self.commandLayout[name].setSpacing(4)
            self.commandLayout[name].setContentsMargins(0, 0, 0, 0)
            self.commandWidget[name].setStyleSheet(
                "padding: 0px; margin: 0px;")
            self.commandLabel[name] = QtWidgets.QLabel(label)
            self.commandLabel[name].setMinimumWidth(180)
            self.commandCheckBox[name] = QtWidgets.QCheckBox()

            self.commandCheckBox[name].setChecked(False)
            self.commandCheckBox[name].setMaximumWidth(20)

            self.commandRunButton[name] = QtWidgets.QPushButton("Run")
            self.commandRunButton[name].setMaximumWidth(40)

            self.commandRunButton[name].clicked.connect(
                partial(self.oneOfs, name))

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
        failedCheckButton = QtWidgets.QPushButton("Check Failed Only")
        failedCheckButton.clicked.connect(self.selectFailed)

        checkAllButton = QtWidgets.QPushButton("Check All")
        checkAllButton.clicked.connect(self.checkAll)
        checkButtonsLayout.addWidget(uncheckAllButton)
        checkButtonsLayout.addWidget(invertCheckButton)
        checkButtonsLayout.addWidget(failedCheckButton)

        checkButtonsLayout.addWidget(checkAllButton)
        return checks

    def closeEvent(self, event):
        self.saveSettings()
        super(UI, self).closeEvent(event)

    def getCategories(self, commands):
        allCategories = set()
        for command in commands.values():
            allCategories.add(command['category'])
        categories = list(allCategories)
        categories.sort(key=str.lower)
        return categories

    def checkState(self, name):
        return self.commandCheckBox[name].checkState()

    def checkAll(self):
        for command in self.commandsList:
            self.commandCheckBox[command].setChecked(True)

    def toggleUI(self, category):
        state = self.categoryWidget[category].isVisible()
        buttonLabel = u'\u21B5' if state else u'\u2193'
        self.categoryCollapse[category].setText(buttonLabel)
        self.categoryWidget[category].setVisible(not state)

    def uncheckAll(self):
        for name in self.commandsList:
            self.commandCheckBox[name].setChecked(False)

    def invertCheck(self):
        for name in self.commandsList.keys():
            self.commandCheckBox[name].setChecked(
                not self.commandCheckBox[name].isChecked())
            
    def clearReport(self):
        self.diagnostics = {}
        for command in self.commandsList.keys():
            self.errorNodesButton[command].setEnabled(False)
            self.commandLabel[command].setStyleSheet('background-color: none;')
        self.reportOutputUI.clear()


    def checkCategory(self, category):
        uncheckedCategoryButtons = []
        categoryButtons = []
        for name in self.commandsList.keys():
            if self.commandsList[name]['category'] == category:
                categoryButtons.append(name)
                if self.commandCheckBox[name].isChecked():
                    uncheckedCategoryButtons.append(name)

        for category in categoryButtons:
            checked = len(uncheckedCategoryButtons) != len(categoryButtons)
            self.commandCheckBox[category].setChecked(checked)

    def filterNodes(self):
        selection = cmds.ls(selection=True, typ="transform")
        if len(selection) > 0:
            nodes = []
            for node in selection:
                if relatives := cmds.listRelatives(node, allDescendents=True, typ="transform"):
                    nodes.extend(relatives)
                nodes.append(node)
        else:
            nodes = self.filterGetAllNodes()
        return nodes

    def filterGetAllNodes(self):
        allNodes = cmds.ls(transforms=True)
        allUsuableNodes = []
        for node in allNodes:
            if node not in {'front', 'persp', 'top', 'side'}:
                allUsuableNodes.append(node)
        return allUsuableNodes
    
    def oneOfs(self, command):
        diagnostics = self.commandToRun([command], self.filterNodes())
        self.diagnostics[command] = diagnostics[command]
        self.createReport()

    def commandToRun(self, commands, nodes):
        diagnostics = {}
        SLMesh = om.MSelectionList()       
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, typ="mesh")
            if shapes:
                SLMesh.add(node)
        for command in commands:
            errors = getattr(
                mcc, command)(nodes, SLMesh)
            diagnostics[command] = errors
        SLMesh.clear()
        return diagnostics

    def createReport(self):
        self.reportOutputUI.clear()
        lastFailed = None
        consolidated = self.consolidatedCheck.isChecked()

        html = ""
        for error in sorted(self.commandsList.keys()):
            if error not in self.diagnostics:
                self.errorNodesButton[error].setEnabled(False)
                self.commandLabel[error].setStyleSheet('background-color: none;')
                continue
            failed = len(self.diagnostics[error]) != 0
            if failed:
                self.errorNodesButton[error].setEnabled(True)
                self.errorNodesButton[error].clicked.connect(partial(self.selectErrorNodes, self.diagnostics[error]))
                self.commandLabel[error].setStyleSheet('background-color: #664444;')
            else:
                self.errorNodesButton[error].setEnabled(False)
                self.commandLabel[error].setStyleSheet('background-color: #446644;')
            label = self.commandsList[error]['label']
            failed = len(self.diagnostics[error]) != 0
            if lastFailed != failed and lastFailed is not None or (failed is True and lastFailed is True):
                html += "<br>"
            lastFailed = failed
            if failed:
                html += f"&#10752; {label}<font color=#9c4f4f> [ FAILED ]</font><br>"
            else:
                html += f"{label}<font color=#64a65a> [ SUCCESS ]</font><br>" 
            
            if failed:
                if consolidated and "." in self.diagnostics[error][0]:
                    store = {}
                    for node in self.diagnostics[error]:
                        name = node.split(".")[0]
                        store[name] = store.get(name, 0) + 1
                    for node in store:
                        word = "issues" if store[node] > 1 else "issue"
                        html += f"&#9492;&#9472; {node} - <font color=#9c4f4f>{store[node]} {word}</font><br>"
                else:
                    for node in self.diagnostics[error]:
                        html += f"&#9492;&#9472; {node}<br>"
        self.reportOutputUI.insertHtml(html)

    def sanityCheck(self):
        checkedCommands = []
        if nodes := self.filterNodes():        
            for name in self.commandsList:
                if self.commandCheckBox[name].isChecked():
                        checkedCommands.append(name)
                diagnostics = self.commandToRun(checkedCommands, nodes)
                self.diagnostics = diagnostics
                self.createReport()
        else:
            self.reportOutputUI.clear()
            self.reportOutputUI.insertHtml("No nodes to check.")


    def selectErrorNodes(self, nodes):
        cmds.select(nodes)

    def saveSettings(self):
        settings = {}
        settings['consolidated'] = self.consolidatedCheck.isChecked()
        settings['commands'] = {}
        for name in self.commandsList:
            settings['commands'][name] = self.commandCheckBox[name].isChecked()
        cmds.optionVar(sv=("modelCheckerSettings", json.dumps(settings)))
    
    def loadSettings(self):
        settings = cmds.optionVar(q="modelCheckerSettings")
        if settings:
            settings = json.loads(settings)
            self.consolidatedCheck.setChecked(settings['consolidated'])
            for name in settings['commands']:
                self.commandCheckBox[name].setChecked(settings['commands'][name])
    
    def selectFailed(self):
        for name in self.commandsList.keys():
            failed = name in self.diagnostics and len(self.diagnostics[name]) > 0
            self.commandCheckBox[name].setChecked(failed)
    
if __name__ == '__main__':
    try:
        win.close()
    except:
        pass
    win = UI(parent=getMainWindow())
    win.show()
    win.raise_()
    