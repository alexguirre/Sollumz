import bpy
from ..nodes.node_tree import NetworkTree
from ...sollumz_helper import SOLLUMZ_OT_base


class SOLLUMZ_OT_MOVE_NETWORK_editor_state_add_transition(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_editor_state_add_transition"
    bl_label = "Add Transition"
    bl_action = bl_label

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == "NODE_EDITOR" and
                space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == 'STATE_MACHINE' and
                space.edit_tree.ui_adding_transition_source_node_name == "" and
                getattr(context, "node", None) is not None)

    def run(self, context):
        node_tree = context.space_data.edit_tree
        node_tree.ui_adding_transition_source_node_name = context.node.name
        # TODO: Add a way to cancel this operation
