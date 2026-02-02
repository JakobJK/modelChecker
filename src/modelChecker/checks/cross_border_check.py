from collections import defaultdict

import maya.api.OpenMaya as om

from maya import cmds

from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

class CrossBorderCheck(ValidationCheckBase):
    name = "cross_border"
    label = "Cross Border"
    category = "UVs"
    node_type = NodeType.UV
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        cross_border = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            faceIt = om.MItMeshPolygon(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
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
                        cross_border[uuid].append(faceIt.index())
                    faceIt.next()
                except:
                    cmds.warning("Face " + str(faceIt.index()) + " has no UVs")
                    faceIt.next()
        return cross_border
