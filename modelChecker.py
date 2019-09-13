from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
from functools import partial

import sys
import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om

def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow

class modelChecker(QtWidgets.QMainWindow):

    def __init__(self, parent=getMainWindow()):
        super(modelChecker, self).__init__(parent)

        # Creates object, Title Name and Adds a QtWidget as our central widget/Main Layout
        self.setObjectName("modelCheckerUI")
        self.setWindowTitle("Model Checker")
        mainLayout = QtWidgets.QWidget(self)
        self.setCentralWidget(mainLayout)

        # Adding a Horizontal layout to divide the UI in two columns
        columns = QtWidgets.QHBoxLayout(mainLayout)

        # Creating 2 vertical layout for the sanity checks and one for the report
        self.report = QtWidgets.QVBoxLayout()
        self.checks = QtWidgets.QVBoxLayout()

        columns.addLayout(self.checks)
        columns.addLayout(self.report)

        # Adding UI ELEMENTS FOR CHECKS
        selectedModelVLayout = QtWidgets.QHBoxLayout()
        self.checks.addLayout(selectedModelVLayout)

        selectedModelLabel = QtWidgets.QLabel("Top Node")
        selectedModelLabel.setMaximumWidth(60)

        self.selectedTopNode_UI = QtWidgets.QLineEdit("")
        self.selectedTopNode_UI.setMaximumWidth(200)

        self.selectedModelNodeButton = QtWidgets.QPushButton("Select")
        self.selectedModelNodeButton.setMaximumWidth(60)
        self.selectedModelNodeButton.clicked.connect(self.setTopNode)

        selectedModelVLayout.addWidget(selectedModelLabel)
        selectedModelVLayout.addWidget(self.selectedTopNode_UI)
        selectedModelVLayout.addWidget(self.selectedModelNodeButton)

        # Adding UI elements to the repport
        self.reportBoxLayout = QtWidgets.QHBoxLayout()
        reportLabel = QtWidgets.QLabel("Report:")

        self.reportBoxLayout.addWidget(reportLabel)
        self.report.addLayout(self.reportBoxLayout)

        self.reportOutputUI = QtWidgets.QPlainTextEdit()

        self.reportOutputUI.setMinimumWidth(600)
        self.report.addWidget(self.reportOutputUI)

        self.checkRunButton = QtWidgets.QPushButton("Run All Checked")
        self.checkRunButton.clicked.connect(self.sanityCheck)

        self.report.addWidget(self.checkRunButton)

        self.clearButton = QtWidgets.QPushButton("Clear")
        self.clearButton.setMaximumWidth(150)
        self.clearButton.clicked.connect(partial(self.reportOutputUI.clear))

        self.reportBoxLayout.addWidget(self.clearButton)

        # Adding the stretch element to the checks UI to get everything at the top
        self.resize(1000,900)
        self.list = [
                'trailingNumbers_naming_1_0',
                'duplicatedNames_naming_1_0',
                'shapeNames_naming_1_0',
                'namespaces_naming_1_0',

                'layers_general_1_1',
                'history_general_1_1',
                'shaders_general_1_1',
                'multipleShapes_general_1_0',
                'unfrozenTransforms_general_1_0',
                'uncenteredPivots_general_1_0',
                'parentGeometry_general_1_0',
                'emptyGroups_general_1_0',

                'triangles_topology_0_0',
                'ngons_topology_0_0',
                'openEdges_topology_0_0',
                'hardEdges_topology_0_0',
                'lamina_topology_0_0',
                'zeroAreaFaces_topology_0_0',
                'zeroLengthEdges_topology_0_0',
                'noneManifoldEdges_topology_0_0',
                'starlike_topology_0_0',

                'selfPenetratingUVs_UVs_0_0',
                'overlappingIslands_UVs_0_0',
                'missingUVs_UVs_0_0',
                'udimRange_UVs_0_0',
                'crossBorder_UVs_0_0'
                ]

        allCategories = []

        for obj in self.list:
            number = obj.split('_')
            allCategories.append(number[1])

        category = set(allCategories)
        self.SLMesh = om.MSelectionList()

        self.categoryLayout = {}
        self.categoryWidget = {}
        self.categoryButton = {}
        self.categoryHeader = {}
        self.categoryCollapse = {}
        self.command = {}
        self.commandWidget = {}
        self.commandLayout = {}
        self.commandLabel = {}
        self.commandCheckBox = {}
        self.errorNodesButton = {}
        self.commandFixButton = {}
        self.commandFix = {}
        self.commandRunButton = {}

        # Create the Categories section!!
        for obj in category:
            self.categoryWidget[obj] = QtWidgets.QWidget()
            self.categoryLayout[obj] = QtWidgets.QVBoxLayout()
            self.categoryHeader[obj] = QtWidgets.QHBoxLayout()
            self.categoryButton[obj] = QtWidgets.QPushButton(obj)
            self.categoryCollapse[obj] = QtWidgets.QPushButton(u'\u2193'.encode('utf-8'))
            self.categoryCollapse[obj].clicked.connect(partial(self.toggleUI, obj))
            self.categoryCollapse[obj].setMaximumWidth(30)
            self.categoryButton[obj].setStyleSheet("background-color: grey; text-transform: uppercase; color: #000000; font-size: 18px;")
            self.categoryButton[obj].clicked.connect(partial(self.checkCategory, obj))
            self.categoryHeader[obj].addWidget(self.categoryButton[obj])
            self.categoryHeader[obj].addWidget(self.categoryCollapse[obj])
            self.categoryWidget[obj].setLayout(self.categoryLayout[obj])
            self.checks.addLayout(self.categoryHeader[obj])
            self.checks.addWidget(self.categoryWidget[obj])

        # Creates the buttons with their settings.
        for obj in self.list:
            new = obj.split('_')
            name = new[0]
            category = new[1]
            check = int(new[2])
            fix = int(new[3])

            self.commandWidget[name] = QtWidgets.QWidget()
            self.commandWidget[name].setMaximumHeight(40)
            self.commandLayout[name] = QtWidgets.QHBoxLayout()

            self.categoryLayout[category].addWidget(self.commandWidget[name])
            self.commandWidget[name].setLayout(self.commandLayout[name])

            self.commandLayout[name].setSpacing(4)
            self.commandLayout[name].setContentsMargins(0,0,0,0)
            self.commandWidget[name].setStyleSheet("padding: 0px; margin: 0px;")
            self.command[name] = name
            self.commandLabel[name] = QtWidgets.QLabel(name)
            self.commandLabel[name].setMinimumWidth(120)
            self.commandCheckBox[name] = QtWidgets.QCheckBox()

            self.commandCheckBox[name].setChecked(check)
            self.commandCheckBox[name].setMaximumWidth(20)

            self.commandRunButton[name] = QtWidgets.QPushButton("Run")
            self.commandRunButton[name].setMaximumWidth(30)

            self.commandRunButton[name].clicked.connect(partial(self.commandToRun, [eval(name)]))

            self.errorNodesButton[name] = QtWidgets.QPushButton("Select Error Nodes")
            self.errorNodesButton[name].setEnabled(False)
            self.errorNodesButton[name].setMaximumWidth(150)

            self.commandFixButton[name] = QtWidgets.QPushButton("Fix")

            if fix == 1:
                self.commandRunButton[name].clicked.connect(partial(self.commandToRun, [eval(name + "_fix")]))

            self.commandFixButton[name].setEnabled(False)
            self.commandFixButton[name].setMaximumWidth(40)

            self.commandLayout[name].addWidget(self.commandLabel[name])
            self.commandLayout[name].addWidget(self.commandCheckBox[name])
            self.commandLayout[name].addWidget(self.commandRunButton[name])
            self.commandLayout[name].addWidget(self.errorNodesButton[name])
            self.commandLayout[name].addWidget(self.commandFixButton[name])

        self.checks.addStretch()

        self.checkButtonsLayout = QtWidgets.QHBoxLayout()
        self.checks.addLayout(self.checkButtonsLayout)


        self.uncheckAllButton = QtWidgets.QPushButton("Uncheck All")
        self.uncheckAllButton.clicked.connect(self.uncheckAll)

        self.invertCheckButton = QtWidgets.QPushButton("Invert")
        self.invertCheckButton.clicked.connect(self.invertCheck)

        self.checkAllButton = QtWidgets.QPushButton("Check All")
        self.checkAllButton.clicked.connect(self.checkAll)

        self.checkButtonsLayout.addWidget(self.uncheckAllButton)
        self.checkButtonsLayout.addWidget(self.invertCheckButton)
        self.checkButtonsLayout.addWidget(self.checkAllButton)

    # Definitions to manipulate the UI
    def setTopNode(self):
        sel = cmds.ls(selection = True)
        self.selectedTopNode_UI.setText(sel[0])

    # Checks the state of a given checkbox
    def checkState(self, name):
        return self.commandCheckBox[name].checkState()


    # Sets all checkboxes to True
    def checkAll(self):
        for obj in self.list:
            new = obj.split('_')
            name = new[0]
            self.commandCheckBox[name].setChecked(True)


    def toggleUI(self, obj):
       state = self.categoryWidget[obj].isVisible()
       if state:
           self.categoryCollapse[obj].setText(u'\u21B5'.encode('utf-8'))
           self.categoryWidget[obj].setVisible(not state)
           self.adjustSize()
       else:
           self.categoryCollapse[obj].setText(u'\u2193'.encode('utf-8'))
           self.categoryWidget[obj].setVisible(not state)


    # Sets all checkboxes to False
    def uncheckAll(self):
        for obj in self.list:
            new = obj.split('_')
            name = new[0]
            self.commandCheckBox[name].setChecked(False)

    # Sets the checkbox to the oppositve of current state
    def invertCheck(self):
        for obj in self.list:
            new = obj.split('_')
            name = new[0]
            self.commandCheckBox[name].setChecked(not self.commandCheckBox[name].isChecked())


    def checkCategory(self, category):

        uncheckedCategoryButtons = []
        categoryButtons = []

        for obj in self.list:
            new = obj.split('_')
            name = new[0]
            cat = new[1]
            if cat == category:
                categoryButtons.append(name)
                if self.commandCheckBox[name].isChecked():
                    uncheckedCategoryButtons.append(name)

        for obj in categoryButtons:
            if len(uncheckedCategoryButtons) == len(categoryButtons):
                self.commandCheckBox[obj].setChecked(False)
            else:
                self.commandCheckBox[obj].setChecked(True)

    ## Filter Nodes
    def filterNodes(self):
        nodes = []
        self.SLMesh.clear()
        allUsuableNodes = []
        allNodes = cmds.ls(transforms = True)
        for obj in allNodes:
            if not obj in {'front', 'persp', 'top', 'side'}:
                allUsuableNodes.append(obj)

        selection = cmds.ls(sl = True)
        topNode = self.selectedTopNode_UI.text()
        if len(selection) > 0:
            nodes = selection
        elif self.selectedTopNode_UI.text() == "":
            nodes = allUsuableNodes
        else:
            if cmds.objExists(topNode):
                nodes = cmds.listRelatives(topNode, allDescendents = True, typ="transform")
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
        # Run FilterNodes
        nodes = self.filterNodes()
        self.reportOutputUI.clear()
        if len(nodes) == 0:
            self.reportOutputUI.insertPlainText("Error - No nodes to check\n")
        else:
            for command in commands:
                # For Each node in filterNodes, run command.
                self.errorNodes = command(self, nodes)
                # Return error nodes
                if self.errorNodes:
                    self.reportOutputUI.insertPlainText(command.func_name + " -- FAILED\n")
                    for obj in self.errorNodes:
                        self.reportOutputUI.insertPlainText("    " + obj + "\n")

                    self.errorNodesButton[command.func_name].setEnabled(True)
                    self.errorNodesButton[command.func_name].clicked.connect(partial(self.selectErrorNodes, self.errorNodes))
                    self.commandLabel[command.func_name].setStyleSheet("background-color: #664444;")
                else:
                    self.commandLabel[command.func_name].setStyleSheet("background-color: #446644;")
                    self.reportOutputUI.insertPlainText(command.func_name + " -- SUCCES\n")
                    self.errorNodesButton[command.func_name].setEnabled(False)

    # Write the report to report UI.
    def sanityCheck(self):
        self.reportOutputUI.clear()
        checkedCommands = []
        for obj in self.list:
            new = obj.split('_')
            name = new[0]
            if self.commandCheckBox[name].isChecked():
                checkedCommands.append(eval(name))
            else:
                self.commandLabel[name].setStyleSheet("background-color: none;")
        if len(checkedCommands) == 0:
            print("You have to select something")
        else:
            self.commandToRun(checkedCommands)

    def selectErrorNodes(self, list):
        cmds.select(list)

    #this definition needs to run the Fix
    def runFix(self, list, command):
        print ("yes")



##
## Helper Functions




#################################################################################################
############################### Backend of the UI starts          ###############################
#################################################################################################

# The UI files to load if a definition doesn't exists for all functions
# The is temporary functions to make the
#

def duplicatedNames(self, list):
    print sys._getframe().f_code.co_name
def trailingNumbers(self, list):
    print sys._getframe().f_code.co_name
def shapeNames(self, list):
    print sys._getframe().f_code.co_name
def namespaces(self, list):
    print sys._getframe().f_code.co_name
def layers(self, list):
    print sys._getframe().f_code.co_name
def history(self, list):
    print sys._getframe().f_code.co_name
def shaders(self, list):
    print sys._getframe().f_code.co_name
def multipleShapes(self, list):
    print sys._getframe().f_code.co_name
def unfrozenTransforms(self, list):
    print sys._getframe().f_code.co_name
def uncenteredPivots(self, list):
    print sys._getframe().f_code.co_name
def parentGeometry(self, list):
    print sys._getframe().f_code.co_name
def ngons(self, list):
    print sys._getframe().f_code.co_name
def triangles(self, list):
    print sys._getframe().f_code.co_name
def emptyGroups(self, list):
    print sys._getframe().f_code.co_name
def hardEdges(self, list):
    print sys._getframe().f_code.co_name
def noneQuads(self, list):
    print sys._getframe().f_code.co_name
def openEdges(self, list):
    print sys._getframe().f_code.co_name
def ButterflyGeometry(self, list):
    print sys._getframe().f_code.co_name
def selfPenetratingUVs(self, list):
    print sys._getframe().f_code.co_name
def overlappingIslands(self, list):
    print sys._getframe().f_code.co_name
def udimRange(self, list):
    print sys._getframe().f_code.co_name
def crossBorder(self, list):
    print sys._getframe().f_code.co_name
def zeroAreaFaces(self, list):
    print sys._getframe().f_code.co_name
def zeroLengthEdges(self, list):
    print sys._getframe().f_code.co_name
def missingUVs(self, list):
    print sys._getframe().f_code.co_name
def lamina(self, list):
    print sys._getframe().f_code.co_name


#    These definitions are temp.
#    If they're not here the UI won't run.


def shapeNames_fix():
    print sys._getframe().f_code.co_name
def namespaces_fix():
    print sys._getframe().f_code.co_name
def layers_fix():
    print sys._getframe().f_code.co_name
def history_fix():
    print sys._getframe().f_code.co_name
def shaders_fix():
    print sys._getframe().f_code.co_name
def unfrozenTransforms_fix():
    print sys._getframe().f_code.co_name
def uncenteredPivots_fix():
    print sys._getframe().f_code.co_name
def emptyGroups_fix():
    print sys._getframe().f_code.co_name
def softenEdge_fix():
    print sys._getframe().f_code.co_name


#
# This is the Naming checks
#
def trailingNumbers(self, list):
    numbers = ['0','1','2','3','4','5','6','7','8','9']
    trailingNumbers = []
    for obj in list:
        if obj[len(obj)-1] in numbers:
            trailingNumbers.append(obj)
    return trailingNumbers

def duplicatedNames(self, list):
    duplicatedNames = []
    for item in list:
    	if '|' in item:
            duplicatedNames.append(item)
    return duplicatedNames

def namespaces(self, list):
    namespaces = []
    for obj in list:
        if ':' in obj:
            namespaces.append(obj)
    return namespaces

def shapeNames(self, list):
    shapeNames = []
    for obj in list:
        new = obj.split('|')
        shape = cmds.listRelatives(obj, shapes = True)
        if shape is not None:
            name = new[-1] + "Shape"
            if not shape[0] == name:
                shapeNames.append(obj)
    return shapeNames

# This is the Topology checks


def triangles(self, list):
    triangles = []
    selIt = om.MItSelectionList(self.SLMesh)
    while not selIt.isDone():
    	faceIt = om.MItMeshPolygon(selIt.getDagPath())
    	objectName = selIt.getDagPath().getPath()
    	while not faceIt.isDone():
    	    numOfEdges = faceIt.getEdges()
    	    if len(numOfEdges) == 3:
    	        faceIndex = faceIt.index()
    	        componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
    	        triangles.append(componentName)
    	    else:
    	        pass
    	    faceIt.next(None)
    	selIt.next()
    return triangles


def ngons(self, list):
    ngons = []
    selIt = om.MItSelectionList(self.SLMesh)
    while not selIt.isDone():
    	faceIt = om.MItMeshPolygon(selIt.getDagPath())
    	objectName = selIt.getDagPath().getPath()
    	while not faceIt.isDone():
    	    numOfEdges = faceIt.getEdges()
    	    if len(numOfEdges) > 4:
    	        faceIndex = faceIt.index()
    	        componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
    	        ngons.append(componentName)
    	    else:
    	        pass
    	    faceIt.next(None)
    	selIt.next()
    return ngons

def hardEdges(self, list):
    hardEdges = []
    selIt = om.MItSelectionList(self.SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.isSmooth == False and edgeIt.onBoundary() == False:
                edgeIndex = edgeIt.index()
                componentName = str(objectName) + '.e[' + str(edgeIndex) + ']'
                hardEdges.append(componentName)
            else:
                pass
            edgeIt.next()
        selIt.next()
    return hardEdges

def lamina(self, list):
    selIt = om.MItSelectionList(self.SLMesh)
    lamina = []
    while not selIt.isDone():
    	faceIt = om.MItMeshPolygon(selIt.getDagPath())
    	objectName = selIt.getDagPath().getPath()
    	while not faceIt.isDone():
    	    laminaFaces = faceIt.isLamina()
    	    if laminaFaces == True:
    	        faceIndex = faceIt.index()
    	        componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
    	        lamina.append(componentName)
    	    else:
    	        pass
    	    faceIt.next(None)
    	selIt.next()
    return lamina

def zeroAreaFaces(self, list):
    zeroAreaFaces = []
    selIt = om.MItSelectionList(self.SLMesh)
    while not selIt.isDone():
    	faceIt = om.MItMeshPolygon(selIt.getDagPath())
    	objectName = selIt.getDagPath().getPath()
    	while not faceIt.isDone():
    	    faceArea = faceIt.zeroArea()
    	    if faceArea == True:
    	        faceIndex = faceIt.index()
    	        componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
    	        zeroAreaFaces.append(componentName)
    	    else:
    	        pass
    	    faceIt.next(None)
    	selIt.next()
    return zeroAreaFaces

def selfPenetratingUVs(self, list):
    selfPenetratingUVs = []
    for obj in list:
        shape = cmds.listRelatives(obj, shapes = True, fullPath = True)
        convertToFaces = cmds.ls(cmds.polyListComponentConversion(shape, tf=True), fl=True)
        overlapping = (cmds.polyUVOverlap(convertToFaces, oc=True ))
        if overlapping is not None:
            for obj in overlapping:
                selfPenetratingUVs.append(obj)
    return selfPenetratingUVs

def noneManifoldEdges(self, list):
    noneManifoldEdges = []
    selIt = om.MItSelectionList(self.SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() > 2:
                edgeIndex = edgeIt.index()
                componentName = str(objectName) + '.e[' + str(edgeIndex) + ']'
                noneManifoldEdges.append(componentName)
            else:
                pass
            edgeIt.next()
        selIt.next()
    return noneManifoldEdges

def openEdges(self, list):
    openEdges = []
    selIt = om.MItSelectionList(self.SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() < 2:
                edgeIndex = edgeIt.index()
                componentName = str(objectName) + '.e[' + str(edgeIndex) + ']'
                openEdges.append(componentName)
            else:
                pass
            edgeIt.next()
        selIt.next()
    return openEdges

def starlike(self, list):
    starlike = []
    selIt = om.MItSelectionList(self.SLMesh)
    while not selIt.isDone():
        polyIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not polyIt.isDone():
            if polyIt.isStarlike() == False:
                polygonIndex = polyIt.index()
                componentName = str(objectName) + '.e[' + str(polygonIndex) + ']'
                starlike.append(componentName)
            else:
                pass
            polyIt.next(None)
        selIt.next()
    return starlike

def missingUVs(self, list):
    missingUVs = []
    selIt = om.MItSelectionList(self.SLMesh)
    while not selIt.isDone():
    	faceIt = om.MItMeshPolygon(selIt.getDagPath())
    	objectName = selIt.getDagPath().getPath()
    	while not faceIt.isDone():
            if faceIt.hasUVs() == False:
                componentName = str(objectName) + '.f[' + str(faceIt.index()) + ']'
                missingUVs.append(componentName)
    	    faceIt.next(None)
    	selIt.next()
    return missingUVs

# This is the general checks

def unfrozenTransforms(self, list):
    unfrozenTransforms = []
    for obj in list:
        translation = cmds.xform(obj, q=True, worldSpace = True, translation = True)
        rotation = cmds.xform(obj, q=True, worldSpace = True, rotation = True)
        scale = cmds.xform(obj, q=True, worldSpace = True, scale = True)
        if not translation == [0.0,0.0,0.0] or not rotation == [0.0,0.0,0.0] or not scale == [1.0,1.0,1.0]:
            unfrozenTransforms.append(obj)
    return unfrozenTransforms

def layers(self, list):
    layers = []
    for obj in list:
        layer = cmds.listConnections(obj, type = "displayLayer")
        if layer is not None:
            layers.append(obj)
    return layers

def shaders(self, list):
    shaders = []
    for obj in list:
        shadingGrps = None
        shape = cmds.listRelatives(obj, shapes = True, fullPath = True)
        if cmds.nodeType(shape) == 'mesh':
            if shape is not None:
                shadingGrps = cmds.listConnections(shape, type='shadingEngine');
            if not shadingGrps[0] == 'initialShadingGroup':
                shaders.append(obj)
    return shaders

def history(self, list):
    history = []
    for obj in list:
        shape = cmds.listRelatives(obj, shapes = True, fullPath = True)
        if shape is not None:
            if cmds.nodeType(shape[0]) == 'mesh':
                historySize = len(cmds.listHistory(shape))
                if historySize > 1:
                    history.append(obj)
    return history

def uncenteredPivots(self, list):
    uncenteredPivots = []
    for obj in list:
        if cmds.xform(obj,q=1,ws=1,rp=1) != [0,0,0]:
            uncenteredPivots.append(obj)
    return uncenteredPivots

def emptyGroups(self, list):
    emptyGroups = []
    for obj in list:
        children = cmds.listRelatives(obj, ad = True)
        if children is None:
            emptyGroups.append(obj)
    return emptyGroups

def parentGeometry(self, list):
    parentGeometry = []
    shapeNode = False
    for obj in list:
        shapeNode = False
        parents = cmds.listRelatives(obj, p = True, fullPath = True)
        if parents is not None:
            for i in parents:
                parentsChildren = cmds.listRelatives(i, fullPath = True)
                for l in parentsChildren:
                    if cmds.nodeType(l) == 'mesh':
                        shapeNode = True
        if shapeNode == True:
            parentGeometry.append(obj)
    return parentGeometry

if __name__ == '__main__':
  try:
      win.close()
  except:
      pass
  win = modelChecker(parent=getMainWindow())
  win.show()
  win.raise_()