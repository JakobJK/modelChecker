from PySide2 import QtWidgets, QtCore, QtGui

from shiboken2 import wrapInstance
from functools import partial
import json
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import modelChecker.modelChecker_commands as mcc
import modelChecker.modelChecker_list as mcl
from modelChecker.__version__ import __version__

def getMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)
    return mainWindow


class UI(QtWidgets.QMainWindow):
    qmwInstance = None
    version = __version__
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
        self.setWindowTitle("Model Checker {}".format(self.version))
        self.diagnostics = {}
        self.currentContextUUID = "Global"
        self.contexts = {
            "Selection": {
                "name": "(Default) Selection",
                "diagnostics": {},
                "nodes": [],
            },
            "Global": {
                "name": "(Default) Global",
                "diagnostics": {},
                "nodes": [],
            },
        }
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
        self.createReport("Global")
        self.consolidatedCheck.stateChanged.connect(self.changeConsolidated)

    def checkSelected(self):
        indexes = self.contextTable.selectionModel().selectedRows()
        for index in indexes:
            rowIdx = index.row()
            contextItem = self.contextTable.item(rowIdx, 1)
            if rowIdx > 1:
                contextItem.setCheckState(QtCore.Qt.Checked)
            else:
                cmds.warning("{} is managed by the modelChecker.".format(contextItem.text()))
    
    def uncheckSelected(self):
        indexes = self.contextTable.selectionModel().selectedRows()
        for index in indexes:
            rowIdx = index.row()
            if rowIdx > 1:
                contextItem = self.contextTable.item(rowIdx, 1)
                contextItem.setCheckState(QtCore.Qt.Unchecked)


    def addSelectedNodesAsNewContexts(self):
        selectedNodes = cmds.ls(selection=True)
        lastContext = None
        for node in selectedNodes:
            parent = self.checkForParent(node)
            if parent:
                msgBox = QtWidgets.QMessageBox()    
                msgBox.setIcon(QtWidgets.QMessageBox.Warning)
                msgBox.setWindowTitle("Warning")
                msgBox.setText("The node you are trying to add ({}) is already part of a context ({}). Do you still wish to add this node as a context? (Not recommended)".format(node, parent))
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                returnValue = msgBox.exec_()
                if returnValue == QtWidgets.QMessageBox.Ok:
                    lastContext = self.addNodeAsContext(node)
            else:
                lastContext = self.addNodeAsContext(node)
        if lastContext:
            self.setRowFromUUID(lastContext)
            

    def addNodeAsContext(self, node):
        uuid = cmds.ls(node, uuid=True)[0]
        allDescendants = self.selectHierachy([uuid])
        uuidItem = QtWidgets.QTableWidgetItem(uuid)

        self.contexts[uuid] = {
            "name": node,
            "diagnostics": {},
            "nodes": allDescendants,
            "tableItem": uuidItem,
        }
        contextItem = QtWidgets.QTableWidgetItem(node)
        nodesItem = QtWidgets.QTableWidgetItem(str(len(allDescendants)))
        testsItem = QtWidgets.QTableWidgetItem("0")
        newRowIdx = self.contextTable.rowCount()
        self.contextTable.insertRow(newRowIdx)
        
        self.contextTable.setItem(newRowIdx, 0, uuidItem)
        self.contextTable.setItem(newRowIdx, 1, contextItem)
        self.contextTable.setItem(newRowIdx, 2, nodesItem)
        self.contextTable.setItem(newRowIdx, 3, testsItem)

        return uuid

    def checkForParent(self, node):
        currentNode = [node]
        while currentNode:
            if currentNode:
                uuid = cmds.ls(currentNode[0], uuid=True)[0]
                if uuid in self.contexts:
                    return currentNode[0]
            currentNode = cmds.listRelatives(currentNode, parent=True)


    def removeSelectedContexts(self):
        idxs = self.contextTable.selectionModel().selectedRows()
        for idx in sorted(idxs, reverse=True):
            uuid = self.contextTable.item(idx.row(), 0).text()            
            if uuid == "Global" or uuid == "Selection":
                continue
            
            node = self.contextTable.item(idx.row(), 1).text()
            try:
                self.contextTable.removeRow(idx.row())
                self.contexts.pop(uuid)
            except:
                cmds.warning("Failed to remove context: {}".format(node))

        if self.currentContextUUID not in self.contexts:        
            lastContext = list(self.contexts.keys())[-1]
            self.setRowFromUUID(lastContext)

    def setCurrentContext(self, row):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.NoModifier:
            uuid = self.contextTable.item(row, 0).text()
            self.currentContextUUID = uuid
            if uuid != "Global" and uuid != "Selection":
                nodeName = cmds.ls(uuid, uuid=True)
                if nodeName:
                    self.contextTable.item(row, 1).setText(nodeName[0])
                else:
                    self.contextTable.item(row, 1).setText("Root node seems to be missing!")
            self.createReport(uuid)
    
    def setRowFromUUID(self, uuid):
        tableItem = self.contexts[uuid]['tableItem']
        row = self.contextTable.row(tableItem)
        self.contextTable.setCurrentItem(self.contextTable.item(row, 0))
        self.setCurrentContext(row)

    def itemSelectionChanged(self):
        if not self.contextTable.selectionModel().selectedRows():
            if self.currentContextUUID in self.contexts:
                self.setRowFromUUID(self.currentContextUUID)

    def buildContextUI(self):
        report = QtWidgets.QVBoxLayout()
        contextWidget = QtWidgets.QWidget()
        contextWidgetLayout = QtWidgets.QVBoxLayout()
        contextWidget.setLayout(contextWidgetLayout)
        self.contextTable = QtWidgets.QTableWidget()
        contextWidgetLayout.addWidget(self.contextTable)
        contextButtonLayout = QtWidgets.QHBoxLayout()

        addContextsBtn = QtWidgets.QPushButton("Add Contexts")
        removeContextsBtn = QtWidgets.QPushButton("Remove Contexts")
        checkSelectedContextsBtn = QtWidgets.QPushButton("Run Checks on Selected Contexts")
        checkAllContextsBtn = QtWidgets.QPushButton("Run Checks on All Added Contexts")
        addContextsBtn.clicked.connect(self.addSelectedNodesAsNewContexts)
        removeContextsBtn.clicked.connect(self.removeSelectedContexts)
        checkSelectedContextsBtn.clicked.connect(self.sanityCheckSelected)
        checkAllContextsBtn.clicked.connect(self.sanityCheckAll)
        contextWidgetLayout.addLayout(contextButtonLayout)
        contextButtonLayout.addWidget(addContextsBtn)
        contextButtonLayout.addWidget(removeContextsBtn)
        contextButtonLayout.addWidget(checkSelectedContextsBtn)
        contextButtonLayout.addWidget(checkAllContextsBtn)

        self.contextTable.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.contextTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        defaultContexts = ["Selection", "Global"]
        contextHeaders = ['UUID', 'CONTEXT', 'NODES', 'TESTS']
        self.contextTable.setColumnCount(len(contextHeaders))
        self.contextTable.setHorizontalHeaderLabels(contextHeaders)
        self.contextTable.verticalHeader().setVisible(False)
        self.contextTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.contextTable.cellClicked.connect(self.setCurrentContext)
        self.contextTable.itemSelectionChanged.connect(self.itemSelectionChanged)

        for idx, context in enumerate(defaultContexts):
            uuidItem = QtWidgets.QTableWidgetItem(context)
            contextItem = QtWidgets.QTableWidgetItem("(Default) {}".format(context))
            self.contexts[context]['tableItem'] = uuidItem 
            nodesItem = QtWidgets.QTableWidgetItem("0")
            testsItem = QtWidgets.QTableWidgetItem("0")
            uuidItem.setFlags(uuidItem.flags() & ~QtCore.Qt.ItemIsEditable)
            contextItem.setFlags(contextItem.flags() & ~QtCore.Qt.ItemIsEditable)
            nodesItem.setFlags(nodesItem.flags() & ~QtCore.Qt.ItemIsEditable)
            testsItem.setFlags(testsItem.flags() & ~QtCore.Qt.ItemIsEditable)

            # if the context is selection, let's make the contextItem uncheckable
            if context == "Selection":
                self.contexts[context]['nodesCount'] = 0
            else:
                self.contexts[context]['nodesCount'] = len(cmds.ls(type="transform")) -4 
            self.contextTable.insertRow(idx)
            self.contextTable.setItem(idx, 0, uuidItem)
            self.contextTable.setItem(idx, 1, contextItem)
            self.contextTable.setItem(idx, 2, nodesItem)
            self.contextTable.setItem(idx, 3, testsItem)

        self.contextTable.setColumnHidden(0, True)
        self.contextTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.reportOutputUI = QtWidgets.QTextEdit()
        self.reportOutputUI.setReadOnly(True)
        self.reportOutputUI.setMinimumWidth(600)

        self.runCurrentButton = QtWidgets.QPushButton("Run Current")
        self.runAllCheckedButton = QtWidgets.QPushButton("Run Checks on Selected / All")
        self.consolidatedCheck = QtWidgets.QCheckBox()

        clearButton = QtWidgets.QPushButton("Clear")
        clearButton.setMaximumWidth(150)
        
        settingsLayout = QtWidgets.QHBoxLayout()
        settingsLayout.addWidget(QtWidgets.QLabel("Consolidated display: "))
        settingsLayout.addStretch()
        settingsLayout.addWidget(self.consolidatedCheck)
        
        runLayout = QtWidgets.QHBoxLayout()
        runLayout.addWidget(QtWidgets.QLabel("Report: "))
        runLayout.addWidget(clearButton)
        runLayout.addWidget(self.runAllCheckedButton)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(contextWidget)
        splitter.addWidget(self.reportOutputUI)
        splitter.setSizes([0, 1])
        report.addLayout(settingsLayout)
        report.addWidget(splitter)
        report.addLayout(runLayout)
        self.runAllCheckedButton.clicked.connect(self.sanityCheckChecked)
        clearButton.clicked.connect(self.clearCurrentReport)
        self.contextTable.setCurrentItem(self.contextTable.item(1, 1))
        return report

    def buildChecksList(self):
        checks = QtWidgets.QVBoxLayout()
        category = self.getCategories(self.commandsList)
        
        for obj in category:
            self.categoryWidget[obj] = QtWidgets.QWidget()
            self.categoryLayout[obj] = QtWidgets.QVBoxLayout()
            self.categoryHeader[obj] = QtWidgets.QHBoxLayout()
            self.categoryButton[obj] = QtWidgets.QPushButton(obj)
            self.categoryCollapse[obj] = QtWidgets.QPushButton(u'\u2193')
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
    
    def clearCurrentReport(self):
        self.clearReportOnContext(self.currentContextUUID)

    def clearReportOnContext(self, contextUUID):
        context = self.contexts[contextUUID]
        context["diagnostics"] = {}
        context["diagnostics"]["nodes"] = 0
        context["diagnostics"]["tests"] = 0
        self.clearRowFromItem(context['tableItem'])
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

    def filterGetAllNodes(self):
        allNodes = cmds.ls(transforms=True, long=True)
        allUsuableNodes = []
        for node in allNodes:
            if node not in {'|front', '|persp', '|top', '|side'}:
                uuid = cmds.ls(node, uuid=True)[0]
                allUsuableNodes.append(uuid)
        return allUsuableNodes
    
    def oneOfs(self, command):
        nodes = self.contexts[self.currentContextUUID]['nodes']
        diagnostics = self.contexts[self.currentContextUUID]['diagnostics']
        newDiagnostics = self.commandToRun([command], nodes)
        diagnostics[command] = newDiagnostics[command]
        self.createReport(self.currentContextUUID)

    def commandToRun(self, commands, nodes):
        diagnostics = {}
        SLMesh = om.MSelectionList()
        nodes = [node for node in nodes if cmds.ls(node, uuid=True)] 
        longNodeNames = [cmds.ls(node, uuid=True)[0] for node in nodes]
        for node in longNodeNames:
            nodeName = cmds.ls(node)
            shapes = cmds.listRelatives(nodeName, shapes=True, typ="mesh")
            if shapes:
                SLMesh.add(node)
        for command in commands:
            type, errors = getattr(
                mcc, command)(nodes, SLMesh)
            diagnostics[command] = {"type": type, "uuids": errors}
        SLMesh.clear()
        return diagnostics

    def parseErrors(self, errors):
        uuids = errors['uuids']
        type =  errors['type']

        if type == 'nodes':
            nodes = []
            for node in errors['uuids']:
                curNode = cmds.ls(node)
                if curNode:
                    nodes.append(curNode[0])
            return nodes
        
        outputErrors = []
        typeMapping = {
            "uv": ".map[{}]",
            "vertex": ".vtx[{}]",
            "edge": ".e[{}]",
            "polygon": ".f[{}]",
         }
        
        for uuid in uuids:
            nodeName = cmds.ls(uuid)
            if nodeName:
                for component in uuids[uuid]:
                    outputErrors.append(nodeName[0] + typeMapping[type].format(component))
        return outputErrors


    def createReport(self, uuid):
        context = self.contexts[uuid]
        diagnostics = context['diagnostics']
        nodes = context['nodes']
        name = context['name']
        self.reportOutputUI.clear()
        lastFailed = None
        consolidated = self.consolidatedCheck.isChecked()
        html = "<h2>{}</h2>".format(name)

        if consolidated or not nodes:
            plural = '' if len(nodes) == 1 else 's'
            html += "&#10752; Node{} checked: {}<br><br>".format(plural, len(nodes))
        else:
            html += "&#10752; Nodes checked:<br>"
            for node in nodes:
                html += "&#9492;&#9472; {}<br>".format(cmds.ls(node)[0])
            html += "<br><br>"
            

        if len(diagnostics) == 0:
            html += "{} - No tests run in this context.".format(self.contexts[self.currentContextUUID]['name'])
            self.reportOutputUI.setHtml(html)
            return

        for error in sorted(self.commandsList.keys()):
            if error not in diagnostics:
                self.errorNodesButton[error].setEnabled(False)
                self.commandLabel[error].setStyleSheet('background-color: none;')
                continue
            
            parsedErrors = self.parseErrors(diagnostics[error])
            failed = len(parsedErrors) != 0
            if failed:
                self.errorNodesButton[error].setEnabled(True)
                self.errorNodesButton[error].clicked.connect(partial(self.selectErrorNodes, diagnostics[error]))
                self.commandLabel[error].setStyleSheet('background-color: #664444;')
            else:
                self.errorNodesButton[error].setEnabled(False)
                self.commandLabel[error].setStyleSheet('background-color: #446644;')
            label = self.commandsList[error]['label']
            failed = len(parsedErrors) != 0
            if lastFailed != failed and lastFailed is not None or (failed is True and lastFailed is True):
                html += "<br>"
            lastFailed = failed
            if failed:
                html += "&#10752; {}<font color=#9c4f4f> [ FAILED ]</font><br>".format(label)
            else:
                html += "{}<font color=#64a65a> [ SUCCESS ]</font><br>".format(label)
            
            if failed:
                if consolidated and len(parsedErrors) > 0:
                    store = {}
                    for node in parsedErrors:
                        name = node.split(".")[0]
                        store[name] = store.get(name, 0) + 1

                    for node in store:
                        word = "issues" if store[node] > 1 else "issue"
                        html += "&#9492;&#9472; {} - <font color=#9c4f4f>{} {}</font><br>".format(node, store[node], word)
                else:
                    for node in parsedErrors:
                        html += "&#9492;&#9472; {}<br>".format(node)
                        
        self.reportOutputUI.insertHtml(html)

    def changeConsolidated(self):
        self.createReport(self.currentContextUUID)

    def selectHierachy(self, nodes):
        hierachy = set()
        for node in nodes:
            nodeName = cmds.ls(node, uuid=True, long=True)[0]
            children = cmds.listRelatives(nodeName, typ="transform", allDescendents=True, fullPath=True)
            if children:
                uuids = [cmds.ls(child, uuid=True)[0] for child in children]
                hierachy.update(uuids)                
            hierachy.add(node)
        return list(hierachy)

    def sanityCheckChecked(self):
        if cmds.ls(selection=True, typ="transform", long=True):
            self.sanityCheck(["Selection"], True)
        else:
            self.sanityCheck(["Global"])

    def sanityCheckAll(self):
        contextsUuids = []
        rowCount = self.contextTable.rowCount()
        for rowIdx in range(rowCount):
            uuidItem = self.contextTable.item(rowIdx, 0)
            uuid = uuidItem.text()
            if uuid == 'Global' or uuid == 'Selection':
                continue
            contextsUuids.append(uuid)
        self.sanityCheck(contextsUuids, False)


    def sanityCheckSelected(self):
        contextsUuids = []
        indexes = self.contextTable.selectionModel().selectedRows()
        for index in indexes:
            rowIdx = index.row()
            uuidItem = self.contextTable.item(rowIdx, 0)
            uuid = uuidItem.text()
            contextsUuids.append(uuid)
        self.sanityCheck(contextsUuids, False)

    def sanityCheck(self, contextsUuids, refreshSelection = True):
        checkedCommands = []
        
        for name in self.commandsList:
            if self.commandCheckBox[name].isChecked():
                checkedCommands.append(name)

        if not checkedCommands:
            cmds.warning("No commands checked")
            return
    
        for contextUUID in contextsUuids:
            if contextUUID == "Global":
                if refreshSelection:
                    nodes = self.filterGetAllNodes()
                else:
                    nodes = self.contexts[contextUUID]['nodes']
            elif contextUUID == "Selection":
                if refreshSelection:
                    selectedNodes = cmds.ls(selection=True, uuid=True, typ="transform")
                    nodes = self.selectHierachy(selectedNodes)
                else:
                    nodes = self.contexts[contextUUID]['nodes']
            else:
                nodes = self.contexts[contextUUID]['nodes']
            
            nodes = [uuid for uuid in nodes if cmds.ls(uuid, uuid=True)]

            if not nodes:
                cmds.warning("No nodes to check")
                return
            
            row = self.contexts[contextUUID]['tableItem'].row()
            self.contextTable.item(row, 3).setText("Running...")
            diagnostics = self.commandToRun(checkedCommands, nodes)
            self.contexts[contextUUID]['nodes'] = nodes
            self.contexts[contextUUID]['diagnostics'] = diagnostics
            self.currentContextUUID = contextUUID
            self.setRowFromItem(self.contexts[contextUUID]['tableItem'])

        self.setRowFromUUID(self.currentContextUUID)

    def selectErrorNodes(self, errors):
        cmds.select(self.parseErrors(errors))
    
    def countErrors(self, diagnostics):
        count = 0
        for error in diagnostics:
            if not diagnostics[error]['uuids']:
                count += 1
        return (count, len(diagnostics))

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
            if 'commands' in settings:
                for name in settings['commands']:
                    self.commandCheckBox[name].setChecked(settings['commands'][name])
                    
    def selectFailed(self):
        diagnostics  = self.contexts[self.currentContextUUID]['diagnostics']
        for name in self.commandsList.keys():
            failed = name in diagnostics and len(diagnostics[name]) > 0
            self.commandCheckBox[name].setChecked(failed)
    
    def setRowFromItem(self, item):
        passed, total = self.countErrors(self.contexts[self.currentContextUUID]['diagnostics'])
        color = "#446644" if passed == total else "#664444"
        row = item.row()
        for column in range(self.contextTable.columnCount()):
            self.contextTable.item(row, column).setBackgroundColor(QtGui.QColor(color))
        nodesItem = self.contextTable.item(row, 2)
        testItem = self.contextTable.item(row, 3)

        nodesItem.setText(str(len(self.contexts[self.currentContextUUID]['nodes'])))
        testItem.setText("{}/{}".format(passed, total))

    def clearRowFromItem(self, item):
        row = item.row()
        for column in range(self.contextTable.columnCount()):
            self.contextTable.item(row, column).setBackgroundColor(QtGui.QColor(0,0,0,0))
        testItem = self.contextTable.item(row, 3)
        testItem.setText("0")
    

if __name__ == '__main__':
    try:
        win.close()
    except:
        pass
    win = UI(parent=getMainWindow())
    win.show()
    win.raise_()
    
