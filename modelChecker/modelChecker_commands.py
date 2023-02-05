import maya.cmds as cmds
import maya.api.OpenMaya as om
import sys

release = cmds.about(version=True)
version = 2023 if 'Preview' in release else int(cmds.about(version=True))
numbers = { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' }

def trailingNumbers(nodes, SLMesh):
    trailingNumbers = []
    for node in nodes:
        if node[-1] in numbers:
            trailingNumbers.append(node)
    return trailingNumbers

def duplicatedNames(nodes, SLMesh):
    duplicatedNames = []
    for node in nodes:
        if '|' in node:
            duplicatedNames.append(node)
    return duplicatedNames


def namespaces(nodes, SLMesh):
    namespaces = []
    for node in nodes:
        if ':' in node:
            namespaces.append(node)
    return namespaces


def shapeNames(nodes, SLMesh):
    shapeNames = []
    for node in nodes:
        new = node.split('|')
        shape = cmds.listRelatives(node, shapes=True)
        if shape:
            shapename = new[-1] + "Shape"
            if shape[0] != shapename:
                shapeNames.append(node)
    return shapeNames

def triangles(_, SLMesh):
    triangles = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) == 3:
                faceIndex = faceIt.index()
                componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
                triangles.append(componentName)
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return triangles


def ngons(_, SLMesh):
    ngons = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) > 4:
                componentName = str(objectName) + '.f[' + str(faceIt.index()) + ']'
                ngons.append(componentName)
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return ngons

def hardEdges(_, SLMesh):
    hardEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.isSmooth == False and edgeIt.onBoundary() == False:
                componentName = str(objectName) + '.e[' + str(edgeIt.index()) + ']'
                hardEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return hardEdges

def lamina(_, SLMesh):
    selIt = om.MItSelectionList(SLMesh)
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
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return lamina


def zeroAreaFaces(_, SLMesh):
    zeroAreaFaces = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            faceArea = faceIt.getArea()
            if faceArea <= 0.00000001:
                componentName = str(objectName) + '.f[' + str(faceIt.index()) + ']'
                zeroAreaFaces.append(componentName)
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return zeroAreaFaces


def zeroLengthEdges(_, SLMesh):
    zeroLengthEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.length() <= 0.00000001:
                componentName = str(objectName) + \
                    '.f[' + str(edgeIt.index()) + ']'
                zeroLengthEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return zeroLengthEdges


def selfPenetratingUVs(transformNodes, SLMesh):
    selfPenetratingUVs = []
    for node in transformNodes:
        shape = cmds.listRelatives(node, shapes=True, fullPath=True)
        convertToFaces = cmds.ls(
            cmds.polyListComponentConversion(shape, tf=True), fl=True)
        overlapping = (cmds.polyUVOverlap(convertToFaces, oc=True))
        if overlapping:
            for node in overlapping:
                selfPenetratingUVs.append(node)
    return selfPenetratingUVs


def noneManifoldEdges(_, SLMesh):
    noneManifoldEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() > 2:
                componentName = str(objectName) + '.e[' + str(edgeIt.index()) + ']'
                noneManifoldEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return noneManifoldEdges


def openEdges(_, SLMesh):
    openEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() < 2:
                componentName = str(objectName) + '.e[' + str(edgeIt.index()) + ']'
                openEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return openEdges


def poles(_, SLMesh):
    poles = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        vertexIt = om.MItMeshVertex(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not vertexIt.isDone():
            if vertexIt.numConnectedEdges() > 5:
                componentName = str(objectName) + \
                    '.vtx[' + str(vertexIt.index()) + ']'
                poles.append(componentName)
            vertexIt.next()
        selIt.next()
    return poles


def starlike(_, SLMesh):
    starlike = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        polyIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not polyIt.isDone():
            if polyIt.isStarlike() == False:
                componentName = str(objectName) + \
                    '.f[' + str(polyIt.index()) + ']'
                starlike.append(componentName)
            if version < 2020:
                polyIt.next(None)
            else:
                polyIt.next()
        selIt.next()
    return starlike

def missingUVs(_, SLMesh):
    missingUVs = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            if faceIt.hasUVs() == False:
                componentName = str(objectName) + \
                    '.f[' + str(faceIt.index()) + ']'
                missingUVs.append(componentName)
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return missingUVs

def uvRange(_, SLMesh):
    uvRange = []
    selIt = om.MItSelectionList(SLMesh)
    mesh = om.MFnMesh(selIt.getDagPath())
    objectName = selIt.getDagPath().getPath()
    Us, Vs = mesh.getUVs()
    for i in range(len(Us)):
        if Us[i] < 0 or Us[i] > 10 or Vs[i] < 0:
            componentName = str(objectName) + '.map[' + str(i) + ']'
            uvRange.append(componentName)
    return uvRange

def onBorder(_, SLMesh):
    onBorder = []
    selIt = om.MItSelectionList(SLMesh)
    mesh = om.MFnMesh(selIt.getDagPath())
    objectName = selIt.getDagPath().getPath()
    Us, Vs = mesh.getUVs()
    for i in range(len(Us)):
        if abs(int(Us[i]) - Us[i]) < 0.00001 or abs(int(Vs[i]) - Vs[i]) < 0.00001:
            componentName = str(objectName) + '.map[' + str(i) + ']'
            onBorder.append(componentName)
    return onBorder

def crossBorder(_, SLMesh):
    crossBorder = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            U, V = set(), set()
            UVs = faceIt.getUVs()
            Us, Vs, = UVs[0], UVs[1]
            for i in range(len(Us)):
                u_add = int(Us[i]) if Us[i] > 0 else int(Us[i]) - 1
                v_add = int(Vs[i]) if Vs[i] > 0 else int(Vs[i]) - 1
                U.add(u_add)
                V.add(v_add)
            if len(U) > 1 or len(V) > 1:
                componentName = str(objectName) + '.f[' + str(faceIt.index()) + ']'
                crossBorder.append(componentName)
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return crossBorder

def unfrozenTransforms(nodes, SLMesh):
    unfrozenTransforms = []
    for node in nodes:
        translation = cmds.xform(
            node, q=True, worldSpace=True, translation=True)
        rotation = cmds.xform(node, q=True, worldSpace=True, rotation=True)
        scale = cmds.xform(node, q=True, worldSpace=True, scale=True)
        if translation != [0.0, 0.0, 0.0] or rotation != [0.0, 0.0, 0.0] or scale != [1.0, 1.0, 1.0]:
            unfrozenTransforms.append(node)
    return unfrozenTransforms

def layers(nodes, _):
    layers = []
    for node in nodes:
        layer = cmds.listConnections(node, type="displayLayer")
        if layer:
            layers.append(node)
    return layers

def shaders(transformNodes, _):
    shaders = []
    for node in transformNodes:
        shape = cmds.listRelatives(node, shapes=True, fullPath=True)
        if cmds.nodeType(shape) == 'mesh' and shape:
            shadingGrps = cmds.listConnections(shape, type='shadingEngine')
            if shadingGrps[0] != 'initialShadingGroup':
                shaders.append(node)
    return shaders

def history(nodes, SLMesh):
    history = []
    for node in nodes:
        shape = cmds.listRelatives(node, shapes=True, fullPath=True)
        if shape and cmds.nodeType(shape[0]) == 'mesh':
            historySize = len(cmds.listHistory(shape))
            if historySize > 1:
                history.append(node)
    return history

def uncenteredPivots(nodes, SLMesh):
    uncenteredPivots = []
    for node in nodes:
        if cmds.xform(node, q=1, ws=1, rp=1) != [0, 0, 0]:
            uncenteredPivots.append(node)
    return uncenteredPivots


def emptyGroups(nodes, SLMesh):
    emptyGroups = []
    for node in nodes:
        children = cmds.listRelatives(node, ad=True)
        if not children:
            emptyGroups.append(node)
    return emptyGroups


def parentGeometry(transformNodes, SLMesh):
    parentGeometry = []
    for node in transformNodes:
        parents = cmds.listRelatives(node, p=True, fullPath=True)
        if parents:
            for parent in parents:
                children = cmds.listRelatives(parent, fullPath=True)
                for parent in children:
                    if cmds.nodeType(parent) == 'mesh':
                        parentGeometry.append(node)
    return parentGeometry
