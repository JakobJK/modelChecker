from abc import ABC
from modelChecker.constants import Severity, NodeType, DataType, COMPONENT_MAPPING
from modelChecker import maya_utility
from maya import cmds


class ValidationCheckBase(ABC):
    name: str
    label: str
    category: str = "General"
    severity: Severity = Severity.MILD
    enabled: bool = True
    depricated: bool = False
    settings = None
    description = "Common description"
    node_type = NodeType.NODE
    
    def run(self, runner):
        """Implemeneted run function."""
        return []
        
    def fix(self):
        """Fix function to be implemented by the extended class."""
        raise NotImplementedError("Fix method not implemented.")
    
    def format_maya_data(self, context):
        if not context:
            return []
        
        if self.node_type == NodeType.NODE:
            return [maya_utility.get_name_from_uuid(uuid) for uuid in context]
        else:
            maya_nodes = []
            for uuid, components in context.items():
                name = maya_utility.get_name_from_uuid(uuid)
                for component in components:
                    if name:
                        maya_nodes.append(name + COMPONENT_MAPPING[self.node_type].format(component))
            return maya_nodes
                    
    def do_select_error_nodes(self, result):
        error_nodes = self.format_maya_data(result.get(self.name))
        cmds.select(error_nodes)        

    def render_maya_data_html(self, context, verbosity_level=2):
        """Render the output to HTML"""
        
        html = ""

        if not context:
            html += f"&#10752; {self.label}<font color=#64a65a> [ SUCCESS ]</font><br>"
        else:
            html += "<br>"
            if verbosity_level == 0:
                word = "issue" if len(context) == 1 else "issues"
                html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] - {len(context)} {word}</font><br>"
            elif verbosity_level == 1:
                html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] </font><br>"
                if self.node_type == NodeType.NODE:
                    for node in context:
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += f"&#9492;&#9472; <font color=#9c4f4f>{node_name}</font><br>"
                else:
                    for node, components in context.items():
                        word = "issue" if len(components) == 1 else "issues"
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += f"&#9492;&#9472; {node_name} - <font color=#9c4f4f>{len(components)} {word}</font><br>"
            elif verbosity_level == 2:
                html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] </font><br>"
                if self.node_type == NodeType.NODE:
                    for node in context:
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += f"&#9492;&#9472; <font color=#9c4f4f>{node_name}</font><br>"
                else:
                    for node, components in context.items():
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += f"&#9492;&#9472; <font color=#9c4f4f>{node_name}</font><br>"
                        for component in components:
                            formatted_component = COMPONENT_MAPPING[self.node_type].format(component)
                            html += f"&nbsp;&nbsp;&#9492;&#9472; <font>{node_name}{formatted_component}</font><br>"

            html += "<br>"
        return html

    
    def has_fix(self) -> bool:
        """Check if the fix method has been implemented."""
        return self.__class__.fix is not ValidationCheckBase.fix
    
    def has_settings(self) -> bool:
        """Check if the implemented class has settings"""
        return self.__class__.settings is not None
    
    def get_name(self):
        return self.__class__.name
        
    def do_run(self, runner):
        """ Wrapper function - may come in handy. """

        result = self.run(runner)
        return result
