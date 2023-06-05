import bpy
from ..nodes.node_tree import NetworkTree
from ...sollumz_helper import SOLLUMZ_OT_base
from ...cwxml.mrf import MoveStateTransition

class SOLLUMZ_OT_MOVE_NETWORK_editor_state_connect_transition(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_editor_state_connect_transition"
    bl_label = "Connect Transition"
    bl_action = bl_label

    @classmethod
    def poll(cls, context):
        space = context.space_data
        node = getattr(context, "node", None)
        return (space.type == "NODE_EDITOR" and
                space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == 'STATE_MACHINE' and
                space.edit_tree.ui_adding_transition_source_node_name != "" and
                node is not None and
                space.edit_tree.ui_adding_transition_source_node_name != node.name)

    def run(self, context):
        node_tree = context.space_data.edit_tree

        source_node = node_tree.nodes[node_tree.ui_adding_transition_source_node_name]
        target_node = context.node

        source_node.add_transition(target_node, MoveStateTransition())

        node_tree.ui_adding_transition_source_node_name = ""
