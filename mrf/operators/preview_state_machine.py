import bpy
from ..nodes.node_tree import NetworkTree
from ...sollumz_helper import SOLLUMZ_OT_base
from ..execution.network_player import NetworkPlayer

class SOLLUMZ_OT_MOVE_NETWORK_preview_state_machine(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_preview_state_machine"
    bl_label = "Preview State Machine"
    bl_action = bl_label

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == "NODE_EDITOR" and
                space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == "STATE_MACHINE" and
                space.edit_tree.network_root is not None and
                space.edit_tree.network_root.selected_armature != -1)

    def run(self, context):
        sm_tree = context.space_data.edit_tree
        root_tree = sm_tree.network_root

        armature = bpy.data.armatures[root_tree.selected_armature]
        if armature is None:
            return False

        if getattr(root_tree, "network_player", None) is None:
            root_tree.network_player = NetworkPlayer(root_tree)

        player = root_tree.network_player
        if player.is_playing:
            player.stop()
        else:
            player.set_armature(armature)
            player.set_state_machine_to_preview(sm_tree)
            player.play()

        return True
