""" Helpful utility functions for maya"""
from maya import cmds

def get_name_from_uuid(uuid, long=True):
    node_name = cmds.ls(uuid, long=long)
    if node_name:
        return node_name[0]
    return None

def get_uuid_from_name(node):
    node_uuid = cmds.ls(node, uuid=True)
    if node_uuid:
        return node_uuid[0]
    return None

def get_uuid_from_shape(shape_node):
    if parent_node := cmds.listRelatives(shape_node, parent=True):
        return get_uuid_from_name(parent_node[0])


def get_all_nodes():
    all_nodes = []    
    for node in cmds.ls(transforms=True, long=True):
        if node not in {'|front', '|persp', '|top', '|side'}:
            children = cmds.listRelatives(node, shapes=True, fullPath=True) or []
            for child in children:
                if cmds.nodeType(child) == 'mayaUsdProxyShape':
                    all_nodes.append(get_uuid_from_name(node))
    return all_nodes


def select_hierachy(nodes):
    hierachy = set()
    for node in nodes:
        node_name = cmds.ls(node, uuid=True, long=True)[0]
        children = cmds.listRelatives(node_name, typ="transform", allDescendents=True, fullPath=True)
        if children:
            uuids = [cmds.ls(child, uuid=True)[0] for child in children]
            hierachy.update(uuids)                
        hierachy.add(node)
    return list(hierachy)
