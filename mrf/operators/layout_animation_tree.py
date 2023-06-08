import bpy
from ..nodes.node_tree import NetworkTree
from ..nodes.layout import layout_animation_tree
from ...sollumz_helper import SOLLUMZ_OT_base


class SOLLUMZ_OT_MOVE_NETWORK_layout_animation_tree(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_layout_animation_tree"
    bl_label = "Layout"
    bl_action = bl_label

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == "NODE_EDITOR" and
                space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == "ANIMATION_TREE")

    def run(self, context):
        anim_tree = context.space_data.edit_tree
        layout_animation_tree(anim_tree)
