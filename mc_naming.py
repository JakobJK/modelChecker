# mc_naming

def nameSpaces():
    cmds.namespace(setNamespace=':')
    nameSpaces = []
    scenesNamespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
    for item in scenesNamespaces:
        if (item !='UI') and (item !='shared'):
            nameSpaces.append(item)
    return nameSpaces
        
def duplicatedNames():
    allTransform = cmds.ls(type='transform')
    duplicatedNames = []
    for item in allTransform:
    	if '|' in item:
            duplicatedNames.append(item)
    return duplicatedNames
    
def checkType():
    allTransform = cmds.ls(type='transform')
    checkType = []
    for item in allTransform:
        if (item.split("_")[-1] == "geo"):
            checkType.append(item)
    return checkType

def invalidShapeNames():
    allTransform = cmds.ls(type='transform')
    invalidShapeNames = []
    for obj in allTransform:
        shape = cmds.listRelatives(obj, c=True, ad=True, type="shape")
        # I have to compare to shape[0] because of unicode.
        if (shape[0] != obj + "Shape"):
            invalidShapeNames.append(shape)
    return invalidShapeNames

