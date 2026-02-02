from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility 
from modelChecker.constants import NodeType
from maya import cmds

TOLERENCE = 0.0001

class OnGridCheck(ValidationCheckBase):
    name = "on_grid"
    label = "On Grid"
    category = "General"
    description = f"Root nodes that are further than {TOLERENCE} from the grid will fail."
    node_type = NodeType.NODE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        output = []
        
        for uuid in runner.get_maya_root_nodes():
            node_name = maya_utility.get_name_from_uuid(uuid)
            bounding_box = cmds.exactWorldBoundingBox(node_name)
            min_y = bounding_box[1]
            if abs(min_y) > TOLERENCE:
                output.append(uuid)
        
        return output
    
