from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from functools import partial
import getpass, datetime, json
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
        super(UI, self).__init__(parent)

        self.setObjectName("ModelCheckerUI")
        self.setWindowTitle('Model Checker' + ' ' + self.version)
        self.diagnostics = {}
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
        self.selectedTopNode_UI.setReadOnly(True)

        clearSelectedNodeButton = QtWidgets.QPushButton("Clear")
        clearSelectedNodeButton.setMaximumWidth(60)
        clearSelectedNodeButton.clicked.connect(lambda: self.selectedTopNode_UI.setText(""))

        selectedModelNodeButton = QtWidgets.QPushButton("Select")
        selectedModelNodeButton.setMaximumWidth(60)
        selectedModelNodeButton.clicked.connect(self.setTopNode)

        selectedModelVLayout.addWidget(selectedModelLabel)
        selectedModelVLayout.addWidget(self.selectedTopNode_UI)
        selectedModelVLayout.addWidget(clearSelectedNodeButton)
        selectedModelVLayout.addWidget(selectedModelNodeButton)
        self.reportOutputUI.setReadOnly(True)
        self.reportOutputUI.setMinimumWidth(600)

        self.checkRunButton = QtWidgets.QPushButton("Run All Checked")
        self.checkRunButton.clicked.connect(self.sanityCheck)

        clearButton = QtWidgets.QPushButton("Clear")
        clearButton.setMaximumWidth(150)
        clearButton.clicked.connect(self.clearReport)

        runLayout = QtWidgets.QHBoxLayout()

        settingsLayout = QtWidgets.QHBoxLayout()

        self.metadataCheck = QtWidgets.QCheckBox()
        self.consolidatedCheck = QtWidgets.QCheckBox()
        settingsLayout.addWidget(QtWidgets.QLabel("Include scene metadata: "))
        settingsLayout.addWidget(self.metadataCheck)
        settingsLayout.addWidget(QtWidgets.QLabel("Consolidated display: "))
        settingsLayout.addWidget(self.consolidatedCheck)
        runLayout.addWidget(QtWidgets.QLabel("Report: "))
        runLayout.addWidget(clearButton)
        runLayout.addWidget(self.checkRunButton)
        report.addLayout(settingsLayout)
        report.addWidget(self.reportOutputUI)
        report.addLayout(runLayout)

        self.resize(1000, 900)
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

        checkAllButton = QtWidgets.QPushButton("Check All")
        checkAllButton.clicked.connect(self.checkAll)
        checkButtonsLayout.addWidget(uncheckAllButton)
        checkButtonsLayout.addWidget(invertCheckButton)
        checkButtonsLayout.addWidget(checkAllButton)
        self.loadSettings()
        self.consolidatedCheck.stateChanged.connect(self.createReport)
        self.metadataCheck.stateChanged.connect(self.createReport)

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

    def setTopNode(self):
        sel = cmds.ls(selection=True)
        if len(sel) == 0:
            cmds.warning("Please select a node")
        else:
            self.selectedTopNode_UI.setText(sel[0])

    def checkState(self, name):
        return self.commandCheckBox[name].checkState()

    def checkAll(self):
        for command in self.commandsList:
            self.commandCheckBox[command].setChecked(True)

    def toggleUI(self, category):
        state = self.categoryWidget[category].isVisible()
        buttonLabel = u'\u21B5' if state else u'\u2193'
        self.adjustSize()
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
            cat = self.commandsList[name]['category']
            if cat == category:
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
                relatives = cmds.listRelatives(node, allDescendents=True, typ="transform")
                if relatives:
                    nodes.extend(relatives)
                nodes.append(node)
        elif self.selectedTopNode_UI.text() == "":
            nodes = self.filterGetAllNodes()
        else:
            nodes = self.filterGetTopNode(self.selectedTopNode_UI.text())
            if not nodes:
                self.reportOutputUI.clear()
                self.reportOutputUI.insertPlainText("Object in Root Node doesn't exists\n")
        return nodes

    def filterGetTopNode(self, topNode):
        nodes = []
        if cmds.objExists(topNode):
            nodes.append(topNode)
            children = cmds.listRelatives(
                topNode, allDescendents=True, typ="transform")
            if children:
                nodes.extend(children)
        else:
            self.selectedTopNode_UI.clear()
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

        if self.metadataCheck.isChecked():
            metadata = self.getMetadata()
            html += "----------------- Scene Metadata -----------------<br>"
            for key in metadata:
                html += f"{key}: {metadata[key]}<br>"
            html += "-----------------------------------------------------<br>"


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

    def getMetadata(self):
        return {
            "user": getpass.getuser(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mayaVersion": cmds.about(iv=True),
            "mayaScene": cmds.file(q=True, sn=True) or "Untitled",
        }

    def sanityCheck(self):
        checkedCommands = []
        nodes = self.filterNodes()
        if not nodes:
            self.reportOutputUI.clear()
            self.reportOutputUI.insertHtml("No nodes to check.")
            return
        for name in self.commandsList:
            if self.commandCheckBox[name].isChecked():
                checkedCommands.append(name)
        diagnostics = self.commandToRun(checkedCommands, nodes)
        self.diagnostics = diagnostics
        self.createReport()

    def selectErrorNodes(self, nodes):
        cmds.select(nodes)

    def saveSettings(self):
        settings = {}
        settings['consolidated'] = self.consolidatedCheck.isChecked()
        settings['metadata'] = self.metadataCheck.isChecked()
        settings['commands'] = {}
        for name in self.commandsList:
            settings['commands'][name] = self.commandCheckBox[name].isChecked()
        cmds.optionVar(sv=("modelCheckerSettings", json.dumps(settings)))
    
    def loadSettings(self):
        settings = cmds.optionVar(q="modelCheckerSettings")
        if settings:
            settings = json.loads(settings)
            self.consolidatedCheck.setChecked(settings['consolidated'])
            if 'metadata' in settings:
                self.metadataCheck.setChecked(settings['metadata'])
            if 'commands' in settings:
                for name in settings['commands']:
                    self.commandCheckBox[name].setChecked(settings['commands'][name])
                    
if __name__ == '__main__':
    try:
        win.close()
    except:
        pass
    win = UI(parent=getMainWindow())
    win.show()
    win.raise_()
    