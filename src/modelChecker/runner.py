""" The Runner is in charge of running all checks"""
from maya import cmds
from modelChecker import maya_utility
from PySide6 import QtWidgets, QtCore

import maya.api.OpenMaya as om

class Runner(QtCore.QObject):
    result_signal = QtCore.Signal(object)
    progress_signal = QtCore.Signal(object)
    error_signal = QtCore.Signal(object)
    
    def __init__(self, checks):
        super().__init__()
        self.current_check = None
        self.current_number_check = 0
        self.scheduled_checks_amount = 0
        
        self.current_context = "all"
        self.contexts = {"all": { "maya": {}}, "selection": { "maya": {}}}
        self.interrupt = False
        self.result_object = {}
        self.nodes = []
        self.cached_data = {}
    
    def _setup_context(self):
        selection = cmds.ls(selection=True, ufe=True, uuid=True)
        all_nodes = selection if selection else maya_utility.get_all_nodes()
        self.current_context = "selection" if selection else "all"
        self.contexts[self.current_context] =  {"maya": {}}
        self.nodes = all_nodes 
        
    
    def stop(self):
        if self.current_check is not None:
            self.interrupt = True
            
    def is_current_context_empty(self):
        if self.current_context not in self.contexts:
            return True
        
        return self.contexts[self.current_context] == {'maya': {}, 'usd': {}}

    
    def run(self, check_widgets, refresh_context: bool = True):
        if refresh_context or self.is_current_context_empty():
            self._setup_context()
        
        if not self.nodes:
            self._error_run("No Nodes to tests")
            return
            
        if not check_widgets:
            self._error_run("No Checks enabled")
            return
        
        context = self.get_context()
        maya_error_object = self.contexts[context]['maya']
        usd_error_object = self.contexts[context]['usd']
                
        self.scheduled_checks_amount = len(check_widgets)

        for idx, check_widget in enumerate(check_widgets):
            check = check_widget.check
            if self.interrupt:
                break
            self.current_check = check
            self.current_number_check = idx + 1
            name = check.get_name()
            maya_result, usd_result = check.do_run(self)
            self._update_progressbars(nodes_total=1, current_node=1)
            had_error = bool(maya_result or usd_result)
            check_widget.update_ui(had_error)
        
        self.result_object = {
        'maya_error_object': maya_error_object,
        'maya_nodes': self.nodes,
        'interrupted': self.interrupt,
        'context': self.current_context,
        'check_widgets': check_widgets,
        'checks_amount': self.scheduled_checks_amount,
        }
        
        self.result_signal.emit(self.result_object)
        self._post_run()
        
    def _post_run(self):
        self.cached_data = {}
        self.current_check = None
        self.interrupt = False
        
    def reset_contexts(self):
        self.nodes = []
        self.contexts = {"all": { "maya": {}, "usd": {}}, "selection": { "maya": {}, "usd": {}}}
        self.current_context = "all"
        self.cached_data = {}
        self.result_object = {}
    
    def get_current_context(self):
        return self.contexts[self.current_context]
    
    def set_current_context(self, context):
        self.current_context = context

    def fix(self, check):
        print("Fix: ", check)
        
    def get_context(self):
        return self.current_context
    
    def get_result_object(self):
        return self.result_object
    
    def get_mesh_shape_iterator(self):
        mesh_shapes = self.get_mesh_shapes()
        nodes_total = len(mesh_shapes)
        for idx, node in enumerate(mesh_shapes):
            self._update_progressbars(nodes_total, idx+1)
            QtWidgets.QApplication.processEvents()
            if self.interrupt:
                break
            yield node
    
    def get_mesh_shapes(self):
        if "mesh_shapes" in self.cached_data:
            return self.cached_data["mesh_shapes"]
        mesh_shapes = []
        node_names = [ maya_utility.get_name_from_uuid(node, long=False) for node in self.nodes ]
        for node in node_names:
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, typ="mesh")
            if shapes:
                mesh_shapes.append(shapes[0])
        
        self.cached_data["mesh_shapes"] = mesh_shapes
        return self.cached_data["mesh_shapes"]
        
    
    def get_mesh_iterator(self):
        if "mesh_selection_list" in self.cached_data:
            sel_mesh = self.cached_data["mesh_selection_list"]
        else:
            sel_mesh = om.MSelectionList()
            for shape in self.get_mesh_shapes():
                sel_mesh.add(shape)
            self.cached_data["mesh_selection_list"] = sel_mesh
        
        iterator = om.MItSelectionList(sel_mesh)
        current_node = 0
        nodes_total = len(self.get_mesh_shapes())
        while not iterator.isDone():
            self._update_progressbars(nodes_total, current_node+1)
            QtWidgets.QApplication.processEvents()
            if self.interrupt:
                break
            dag_path = iterator.getDagPath()
            yield dag_path
            current_node += 1
            iterator.next()
            
    
    def get_maya_root_nodes(self):
        root_nodes = []
        
        for node in self.nodes:
            node_name = maya_utility.get_name_from_uuid(node)
            parent = cmds.listRelatives(node_name, parent=True)
            if parent is None:
                root_nodes.append(node)
                
        nodes_total = len(root_nodes)
        for idx, node in enumerate(root_nodes):
            self._update_progressbars(nodes_total, idx+1)
            QtWidgets.QApplication.processEvents()
            if self.interrupt:
                break
            yield node
                
    def get_maya_nodes(self):
        """Iterator to be called by the check functions!"""
        nodes_total = len(self.nodes)
        for idx, node in enumerate(self.nodes):
            self._update_progressbars(nodes_total, idx+1)
            QtWidgets.QApplication.processEvents()
            if self.interrupt:
                break
            yield node
            
    
    def _update_progressbars(self, nodes_total, current_node):
        label = self.current_check.label
        total_checks = self.scheduled_checks_amount
        current_check = self.current_number_check
        self.progress_signal.emit({
            "label": label,
            "total_checks": total_checks,
            "current_check": current_check,
            "nodes_total": nodes_total,
            "current_node": current_node
            })
        
    def _error_run(self, message):
        self.error_signal.emit({"error": message})
