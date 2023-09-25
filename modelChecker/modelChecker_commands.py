from collections import defaultdict

import maya.cmds as cmds
import maya.api.OpenMaya as om

def trailingNumbers(nodes, _):
    trailingNumbers = []
    for node in nodes:
        if node[-1].isdigit():
            trailingNumbers.append(node)
    return trailingNumbers

def duplicatedNames(nodes, _):
    nodesByShortName = defaultdict(list)
    for node in nodes:
        name = node.rsplit('|', 1)[-1]
        nodesByShortName[name].append(node)
        
    invalid = []
    for name, shortNameNodes in nodesByShortName.items():
        if len(shortNameNodes) > 1:
            invalid.extend(shortNameNodes)
    return invalid


def namespaces(nodes, _):
    namespaces = []
    for node in nodes:
        if ':' in node:
            namespaces.append(node)
    return namespaces


def shapeNames(nodes, _):
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
        objectName = selIt.getDagPath().fullPathName()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) == 3:
                faceIndex = faceIt.index()
                componentName = "{}.f[{}]".format(str(objectName), str(faceIndex))
                triangles.append(componentName)
            faceIt.next()
        selIt.next()
    return triangles


def ngons(_, SLMesh):
    ngons = []
    if SLMesh.isEmpty():
        return ngons
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) > 4:
                componentName = "{}.f[{}]".format(str(objectName), str(faceIt.index()))
                ngons.append(componentName)
            faceIt.next()
        selIt.next()
    return ngons

def hardEdges(_, SLMesh):
    hardEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not edgeIt.isDone():
            if edgeIt.isSmooth is False and edgeIt.onBoundary() is False:
                componentName = "{}.e[{}]".format(str(objectName), str(edgeIt.index()))
                hardEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return hardEdges

def lamina(_, SLMesh):
    selIt = om.MItSelectionList(SLMesh)
    lamina = []
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not faceIt.isDone():
            laminaFaces = faceIt.isLamina()
            if laminaFaces is True:
                componentName = "{}.f[{}]".format(str(objectName), str(faceIt.index()))
                lamina.append(componentName)
            faceIt.next()
        selIt.next()
    return lamina


def zeroAreaFaces(_, SLMesh):
    zeroAreaFaces = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not faceIt.isDone():
            faceArea = faceIt.getArea()
            if faceArea <= 0.00000001:
                componentName = "{}.f[{}]".format(str(objectName), str(faceIt.index()))
                zeroAreaFaces.append(componentName)
            faceIt.next()
        selIt.next()
    return zeroAreaFaces


def zeroLengthEdges(_, SLMesh):
    zeroLengthEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not edgeIt.isDone():
            if edgeIt.length() <= 0.00000001:
                componentName = "{}.f[{}]".format(str(objectName), str(edgeIt.index()))
                zeroLengthEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return zeroLengthEdges

def selfPenetratingUVs(transformNodes, _):
    selfPenetratingUVs = []
    for node in transformNodes:
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True, type="mesh", noIntermediate=True)
        if shapes:
            overlapping = cmds.polyUVOverlap("{}.f[*]".format(shapes[0]), oc=True)
            if overlapping:
                selfPenetratingUVs.extend(overlapping)
    return selfPenetratingUVs

def noneManifoldEdges(_, SLMesh):
    noneManifoldEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() > 2:
                componentName = "{}.e[{}]".format(str(objectName), str(edgeIt.index()))
                noneManifoldEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return noneManifoldEdges


def openEdges(_, SLMesh):
    openEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() < 2:
                componentName = "{}.e[{}]".format(str(objectName), str(edgeIt.index()))
                openEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return openEdges


def poles(_, SLMesh):
    poles = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        vertexIt = om.MItMeshVertex(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not vertexIt.isDone():
            if vertexIt.numConnectedEdges() > 5:
                componentName = "{}.vtx[{}]".format(str(objectName), str(vertexIt.index()))
                poles.append(componentName)
            vertexIt.next()
        selIt.next()
    return poles


def starlike(_, SLMesh):
    starlike = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        polyIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not polyIt.isDone():
            if polyIt.isStarlike() is False:
                componentName = "{}.f[{}]".format(str(objectName), str(polyIt.index()))
                starlike.append(componentName)
            polyIt.next()
        selIt.next()
    return starlike

def missingUVs(_, SLMesh):
    if SLMesh.isEmpty():
        return []
    missingUVs = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not faceIt.isDone():
            if faceIt.hasUVs() is False:
                componentName = "{}.f[{}]".format(str(objectName), str(faceIt.index()))
                missingUVs.append(componentName)
            faceIt.next()
        selIt.next()
    return missingUVs

def uvRange(_, SLMesh):
    if SLMesh.isEmpty():
        return []
    uvRange = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        mesh = om.MFnMesh(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        Us, Vs = mesh.getUVs()
        for i in range(len(Us)):
            if Us[i] < 0 or Us[i] > 10 or Vs[i] < 0:
                componentName = "{}.map[{}]".format(str(objectName), str(i))
                uvRange.append(componentName)
        selIt.next()
    return uvRange

def onBorder(_, SLMesh):
    if SLMesh.isEmpty():
        return []
    onBorder = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        mesh = om.MFnMesh(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        Us, Vs = mesh.getUVs()
        for i in range(len(Us)):
            if abs(int(Us[i]) - Us[i]) < 0.00001 or abs(int(Vs[i]) - Vs[i]) < 0.00001:
                componentName = "{}.map[{}]".format(str(objectName), str(i))
                onBorder.append(componentName)
        selIt.next()
    return onBorder

def crossBorder(_, SLMesh):
    crossBorder = []
    if SLMesh.isEmpty():
        return crossBorder
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().fullPathName()
        while not faceIt.isDone():
            U, V = set(), set()
            try:
                UVs = faceIt.getUVs()
                Us, Vs, = UVs[0], UVs[1]
                for i in range(len(Us)):
                    uAdd = int(Us[i]) if Us[i] > 0 else int(Us[i]) - 1
                    vAdd = int(Vs[i]) if Vs[i] > 0 else int(Vs[i]) - 1
                    U.add(uAdd)
                    V.add(vAdd)
                if len(U) > 1 or len(V) > 1:
                    componentName = "{}.f[{}]".format(str(objectName), str(faceIt.index()))
                    crossBorder.append(componentName)
                faceIt.next()
            except:
                cmds.warning("Face " + str(faceIt.index()) + " has no UVs")
                faceIt.next()
        selIt.next()
    return crossBorder

def unfrozenTransforms(nodes, _):
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

def history(nodes, _):
    history = []
    for node in nodes:
        shape = cmds.listRelatives(node, shapes=True, fullPath=True)
        if shape and cmds.nodeType(shape[0]) == 'mesh':
            historySize = len(cmds.listHistory(shape))
            if historySize > 1:
                history.append(node)
    return history

def uncenteredPivots(nodes, _):
    uncenteredPivots = []
    for node in nodes:
        if cmds.xform(node, q=1, ws=1, rp=1) != [0, 0, 0]:
            uncenteredPivots.append(node)
    return uncenteredPivots


def emptyGroups(nodes, _):
    emptyGroups = []
    for node in nodes:
        if not cmds.listRelatives(node, ad=True):
            emptyGroups.append(node)
    return emptyGroups

def parentGeometry(transformNodes, _):
    parentGeometry = []
    for node in transformNodes:
        parents = cmds.listRelatives(node, p=True, fullPath=True)
        if parents:
            for parent in parents:
                children = cmds.listRelatives(parent, fullPath=True)
                for child in children:
                    if cmds.nodeType(child) == 'mesh':
                        parentGeometry.append(node)
    return parentGeometry