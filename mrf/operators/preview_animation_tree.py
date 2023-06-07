import bpy
from ..nodes.node_tree import NetworkTree
from ...sollumz_helper import SOLLUMZ_OT_base
from ..execution.network_player import NetworkPlayer

class SOLLUMZ_OT_MOVE_NETWORK_preview_animation_tree(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_preview_animation_tree"
    bl_label = "Preview Animation Tree"
    bl_action = bl_label

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == "NODE_EDITOR" and
                space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == "ANIMATION_TREE" and
                space.edit_tree.network_root is not None and
                space.edit_tree.network_root.selected_armature != -1)

    def run(self, context):
        anim_tree = context.space_data.edit_tree
        root_tree = anim_tree.network_root

        armature = bpy.data.armatures[root_tree.selected_armature]
        if armature is None:
            return {"FINISHED"}

        if getattr(root_tree, "network_player", None) is None:
            root_tree.network_player = NetworkPlayer(root_tree)

        player = root_tree.network_player
        if player.is_playing:
            player.stop()
        else:
            player.set_animation_tree_to_preview(anim_tree)
            player.set_armature(armature)
            player.play()
