import bpy
from ..nodes.node_tree import NetworkTree
from ...sollumz_helper import SOLLUMZ_OT_base
from ..execution.network_player import NetworkPlayer

class SOLLUMZ_OT_MOVE_NETWORK_delete_network_parameter(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_delete_network_parameter"
    bl_label = "Delete MoVE Network Parameter"
    bl_action = bl_label

    parameter_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == "NODE_EDITOR" and
                space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname)

    def run(self, context):
        node_tree = context.space_data.edit_tree
        network = node_tree.network_root or node_tree
        network.network_parameters.remove(self.parameter_name)
        return True
