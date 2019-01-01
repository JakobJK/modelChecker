from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
from functools import partial

import sys
import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMayaUI as omui

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
                'namingConvention_naming_1_0',
                'duplicatedNames_naming_1_0',
                'shapeNames_naming_1_1',
                'namespaces_naming_1_1',

                'layers_general_1_1',
                'history_general_1_1',
                'shaders_general_1_1',
                'multipleShapes_general_1_0',
                'unfrozenTransforms_general_1_1',
                'uncenteredPivots_general_1_1',
                'parentGeometry_general_1_0',
                'emptyGroups_general_1_1',
                'softenEdge_general_1_1',

                'triangles_topology_0_0',
                'ngons_topology_0_0',
                'openEdges_topology_0_0',
                'lamina_topology_0_0',
                'zeroAreaFaces_topology_0_0',
                'zeroLengthEdges_topology_0_0',

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

        self.categoryLayout = {}
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
            self.categoryLayout[obj] = QtWidgets.QVBoxLayout()
            self.categoryHeader[obj] = QtWidgets.QHBoxLayout()
            self.categoryButton[obj] = QtWidgets.QPushButton(obj)
            self.categoryCollapse[obj] = QtWidgets.QPushButton("-")
            self.categoryCollapse[obj].setMaximumWidth(30)
            self.categoryButton[obj].setStyleSheet("background-color: grey; text-transform: uppercase; color: #000000; font-size: 18px;")
            self.categoryButton[obj].clicked.connect(partial(self.checkCategory, obj))

            self.categoryHeader[obj].addWidget(self.categoryButton[obj])
            self.categoryHeader[obj].addWidget(self.categoryCollapse[obj])
            self.checks.addLayout(self.categoryHeader[obj])
            self.checks.addLayout(self.categoryLayout[obj])

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

            self.commandRunButton[name].clicked.connect(partial(self.commandToRun, eval(name)))

            self.errorNodesButton[name] = QtWidgets.QPushButton("Select Error Nodes")
            self.errorNodesButton[name].setEnabled(False)
            self.errorNodesButton[name].setMaximumWidth(150)

            self.commandFixButton[name] = QtWidgets.QPushButton("Fix")

            if fix == 1:
                self.commandRunButton[name].clicked.connect(partial(self.commandToRun, eval(name + "_fix")))

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
                nodes.append(topNode)
            else:
                response = "Object in Top Node doesn't exists\n"
                self.reportOutputUI.clear()
                self.reportOutputUI.insertPlainText(response)
        return nodes

    def commandToRun(self, command):
        # Run FilterNodes
        nodes = self.filterNodes()
        if len(nodes) == 0:

            self.reportOutputUI.insertPlainText("Error - No nodes to check\n")

        else:
            # For Each node in filterNodes, run command.
            self.errorNodes = command(nodes)
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
        nodes = self.filterNodes()
        if len(nodes) == 0:
            self.reportOutputUI.insertPlainText("Error - No nodes to check")
        else:
            for obj in self.list:
                new = obj.split('_')
                name = new[0]
                if self.commandCheckBox[name].isChecked():
                    self.commandToRun(eval(name))
                else:
                    self.commandLabel[name].setStyleSheet("background-color: none;")

    def selectErrorNodes(self, list):
        cmds.select(list)

    #this definition needs to run the Fix
    def runFix(self, list, command):
        print "yes"


#################################################################################################
############################### Backend of the UI starts          ###############################
#################################################################################################

# The UI files to load if a definition doesn't exists for all functions
# The is temporary functions to make the
#

def duplicatedNames(list):
    print sys._getframe().f_code.co_name
def namingConvention(list):
    print sys._getframe().f_code.co_name
def shapeNames(list):
    print sys._getframe().f_code.co_name
def namespaces(list):
    print sys._getframe().f_code.co_name
def layers(list):
    print sys._getframe().f_code.co_name
def history(list):
    print sys._getframe().f_code.co_name
def shaders(list):
    print sys._getframe().f_code.co_name
def multipleShapes(list):
    print sys._getframe().f_code.co_name
def unfrozenTransforms(list):
    print sys._getframe().f_code.co_name
def uncenteredPivots(list):
    print sys._getframe().f_code.co_name
def parentGeometry(list):
    print sys._getframe().f_code.co_name
def ngons(list):
    print sys._getframe().f_code.co_name
def triangles(list):
    print sys._getframe().f_code.co_name
def emptyGroups(list):
    print sys._getframe().f_code.co_name
def softenEdge(list):
    print sys._getframe().f_code.co_name
def noneQuads(list):
    print sys._getframe().f_code.co_name
def openEdges(list):
    print sys._getframe().f_code.co_name
def ButterflyGeometry(list):
    print sys._getframe().f_code.co_name
def selfPenetratingUVs(list):
    print sys._getframe().f_code.co_name
def overlappingIslands(list):
    print sys._getframe().f_code.co_name
def udimRange(list):
    print sys._getframe().f_code.co_name
def crossBorder(list):
    print sys._getframe().f_code.co_name
def zeroAreaFaces(list):
    print sys._getframe().f_code.co_name
def zeroLengthEdges(list):
    print sys._getframe().f_code.co_name
def missingUVs(list):
    print sys._getframe().f_code.co_name
def lamina(list):
    print sys._getframe().f_code.co_name


#    These definitions are temp.
#    If they're not here the UI won't run.


def shapeNames_fix():
    print "lol"
def namespaces_fix():
    print "lol"
def layers_fix():
    print "lol"
def history_fix():
    print "lol"
def shaders_fix():
    print "lol"
def unfrozenTransforms_fix():
    print "lol"
def uncenteredPivots_fix():
    print "lol"
def emptyGroups_fix():
    print "lol"
def softenEdge_fix():
    print "lol"


#
# This is the Naming checks
#

def duplicatedNames(list):
    duplicatedNames = []
    for item in list:
    	if '|' in item:
            duplicatedNames.append(item)
    return duplicatedNames

def namespaces(list):
    namespaces = []
    for obj in list:
        if ':' in obj:
            namespaces.append(obj)
    return namespaces

def shapeNames(list):
    shapeNames = []
    for obj in list:
        new = obj.split('|')
        shape = cmds.listRelatives(obj, shapes = True)
        if shape is not None:
            name = new[-1] + "Shape"
            if not shape[0] == name:
                shapeNames.append(obj)
    return shapeNames

#
# This is the Topology checks
#


def triangles(list):
    triangles = []
    for item in list:
        convertItemToFaces = cmds.ls(cmds.polyListComponentConversion(item, tf=True), fl=True)
        for eachFace in convertItemToFaces:
            checkIfTri = pm.PyNode(eachFace).numTriangles()
            if checkIfTri == 1:
                triangles.append(eachFace)
    return triangles


def ngons(list):
    ngons = []
    for item in list:
        convertItemToFaces = cmds.ls(cmds.polyListComponentConversion(item, tf=True), fl=True)
        for eachFace in convertItemToFaces:
            getFaceEdges = pm.PyNode(eachFace).getEdges()
            if len(getFaceEdges) > 4:
                ngons.append(eachFace)
    return ngons

def zeroLengthEdges(list):
    zeroLengthEdges = []
    for item in list:
        convertItemToEdges = cmds.ls(cmds.polyListComponentConversion(item, te=True), fl=True)
        for eachEdge in convertItemToEdges:
            checkEdgeLength = pm.PyNode(eachEdge).getLength()
            if checkEdgeLength < 0.0000000001:
                zeroLengthEdges.append(eachEdge)
    return zeroLengthEdges

#
# This is the UV checks
#

def selfPenetratingUVs(list):
    selfPenetratingUVs = []
    for obj in list:
        shape = cmds.listRelatives(obj, shapes = True, fullPath = True)
        convertToFaces = cmds.ls(cmds.polyListComponentConversion(shape, tf=True), fl=True)
        overlapping = (cmds.polyUVOverlap(convertToFaces, oc=True ))
        if overlapping is not None:
            for obj in overlapping:
                selfPenetratingUVs.append(obj)
    return selfPenetratingUVs

def missingUVs(list):
    missingUVsList = []
    for item in list:
        convertItemToFaces = cmds.ls(cmds.polyListComponentConversion(item, tf=True), fl=True)
        for eachFace in convertItemToFaces:
            checkForMissingUVs = pm.PyNode(eachFace).hasUVs()
            if checkForMissingUVs == False:
                missingUVsList.append(eachFace)
    return missingUVsList

#
# This is the general checks
#

def unfrozenTransforms(list):
    unfrozenTransforms = []
    for obj in list:
        translation = cmds.xform(obj, q=True, worldSpace = True, translation = True)
        rotation = cmds.xform(obj, q=True, worldSpace = True, rotation = True)
        scale = cmds.xform(obj, q=True, worldSpace = True, scale = True)
        if not translation == [0.0,0.0,0.0] or not rotation == [0.0,0.0,0.0] or not scale == [1.0,1.0,1.0]:
            unfrozenTransforms.append(obj)
    return unfrozenTransforms

def layers(list):
    layers = []
    for obj in list:
        layer = cmds.listConnections(obj, type = "displayLayer")
        if layer is not None:
            layers.append(obj)
    return layers

def shaders(list):
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

def history(list):
    history = []
    for obj in list:
        shape = cmds.listRelatives(obj, shapes = True, fullPath = True)
        if shape is not None:
            if cmds.nodeType(shape[0]) == 'mesh':
                historySize = len(cmds.listHistory(shape))
            if historySize > 1:
                history.append(obj)
    return history

def emptyGroups(list):
    emptyGroups = []
    for obj in list:
        children = cmds.listRelatives(obj, ad = True)
        if children is None:
            emptyGroups.append(obj)
    return emptyGroups

def parentGeometry(list):
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

if __name__ = '__main__':
  try:
      win.close()
  except:
      pass
  win = modelChecker(parent=getMainWindow())
  win.show()
  win.raise_()
