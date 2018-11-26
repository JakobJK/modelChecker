## Checks the naming convention

## position_name_material_iterator_nodeType
## Example: 
## c_body_skin_0001_geo
## c_model_001_grp

def nameElement():
    return nameElement

def nodeType():
    allTransform = cmds.ls(type='transform')
    allowedTypes = ['geo', 'gep', '']
    nodeType = []
    for item in allTransform:
        if (item.split("_")[-1] == "geo"):
            nodeType.append(item)
    return nodeType

def material():
    allowedMaterials = ['skin','metal','leather', ]
    return material

def iterator():
    return iterator

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


def invalidShapeNames():
    allTransform = cmds.ls(type='transform')
    invalidShapeNames = []
    for obj in allTransform:
        shape = cmds.listRelatives(obj, c=True, ad=True, type="shape")
        # I have to compare to shape[0] because of unicode.
        if (shape[0] != obj + "Shape"):
            invalidShapeNames.append(shape)
    return invalidShapeNames

