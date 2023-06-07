import bpy
from ..nodes.node_tree import NetworkTree
from ...sollumz_helper import SOLLUMZ_OT_base
from ..execution.network_player import NetworkPlayer

class SOLLUMZ_OT_MOVE_NETWORK_preview(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_preview"
    bl_label = "Preview MoVE Network"
    bl_action = bl_label

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == "NODE_EDITOR" and
                space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.selected_armature != -1)

    def run(self, context):
        node_tree = context.space_data.edit_tree
        root_node_tree = node_tree.network_root or node_tree

        armature = bpy.data.armatures[node_tree.selected_armature]
        if armature is None:
            return {"FINISHED"}

        if getattr(root_node_tree, "network_player", None) is None:
            root_node_tree.network_player = NetworkPlayer(root_node_tree)

        player = root_node_tree.network_player
        if player.is_playing:
            player.stop()
        else:
            player.set_armature(armature)
            player.play()
