import bpy


# NodeTree code based on: https://github.com/atticus-lv/simple_node_tree
class NodeTree(bpy.types.NodeTree):
    bl_idname = "SOLLUMZ_NT_MOVE_NETWORK"
    bl_label = "MoVE Network Editor"
    bl_icon = "ONIONSKIN_ON"