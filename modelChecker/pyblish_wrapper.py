import modelChecker.modelChecker_list as command_list
import modelChecker.modelChecker_commands as mcc
import pyblish.api
import maya.api.OpenMaya as om
import maya.cmds as cmds

FAMILIES = ['mesh', 'long_name']

class CollectMeshNames(pyblish.api.Collector):
    """collect long mesh names"""

    # pyblish plugin attributes
    hosts = ['maya']
    label = 'collect meshnames'
    optional = True

    def process(self, context):
        long_mesh_names = cmds.ls(type='mesh', objectsOnly=True, noIntermediate=True, long=True)
        for long_mesh_name in long_mesh_names:
            short_mesh_name = long_mesh_name.rsplit('|', 1)[1]  # get short name of the node
            instance = context.create_instance(short_mesh_name, icon="cubes", families=FAMILIES)
            instance.append(long_mesh_name)


# since some functions use the meshname, and some use SLMesh, we need to create a SLMesh from the meshname
def create_SLMesh_from_nodes(nodes):
    SLMesh = om.MSelectionList()
    for node in nodes:
        SLMesh.add(node)
    return SLMesh


class ActionSelect(pyblish.api.Action):
    label = "Select failed"
    on = "failedOrWarning"
    icon = "hand-o-up"  # Icon from Awesome Icon

    def process(self, context, plugin):
        errors = context.data[plugin.label]  # list of strings, ex. ['pCube2.f[0]',...]
        print(errors)
        cmds.select(errors)


def plugin_factory(func, label_input, category, doc, **kwargs):
    """
    create a costum class that loads the functions from check_core in pyblish as plugins.
    :param str func: name of function/command we want to wrap in a pyblish plugin
    :param str label_input: label of the command

    # not used -------
    :param str category:  category of the command
    :param dict **kwargs: additional keyword arguments we want to pass to the function when run

    :return custom class type, inherits from pyblish.api.Validator
    :rtype: Class
    """

    class ValidationPlugin(pyblish.api.Validator):
        label = str(label_input)  # copy string to prevent mutation issues
        hosts = ["maya"]
        families = FAMILIES
        optional = True
        actions = [ActionSelect]
        _func = [func]  # we can't store func directly or it will pass self when running self.func()

        def process(self, instance, context):
            mesh_names = instance[:]
            for mesh_name in mesh_names:
                try:
                    command = self._func[0]
                    nodes = [mesh_name]
                    SLMesh = create_SLMesh_from_nodes(nodes)
                    errors = getattr(mcc, command)(nodes, SLMesh) # errorNodes

                    # errors = func(mesh_name, **kwargs)
                except Exception as ex:
                    errors = [mesh_name]

                context.data[self.label] = errors  # save failed results for reuse later
                assert not errors, 'check failed on:' + str(errors)

    ValidationPlugin.__name__ = 'validate_' + func
    ValidationPlugin.__doc__ = doc

    return ValidationPlugin


# create pyblish plugins dynamically, and add them to this module it's variables so that pyblish's discover function can find them
module_variable_dict = globals()
for data in command_list.mcCommandsList:
    command = data['func']
    label = data['label']
    category = data['category']
    doc = data.get('description', None)

    variable_name = 'validate_' + command + '_plugin'
    pyblish_plugin = plugin_factory(command, label, category, doc)
    module_variable_dict[variable_name] = pyblish_plugin
