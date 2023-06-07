import bpy

NetworkTreeTypes = [
    ("ROOT", "Root", "Root tree", 0),
    ("ANIMATION_TREE", "Animation Tree", "Animation tree", 1),
    ("STATE_MACHINE", "State Machine", "State machine transition graph", 2),
]


class NetworkTree(bpy.types.NodeTree):
    bl_idname = "SOLLUMZ_NT_MOVE_NETWORK_NetworkTree"
    bl_label = "MoVE Network Editor"
    bl_icon = "ONIONSKIN_ON"

    network_tree_type: bpy.props.EnumProperty(name="Type", items=NetworkTreeTypes)
    network_root: bpy.props.PointerProperty(name="Network Root", type=bpy.types.NodeTree)

    ui_active_transition_source_node_name: bpy.props.StringProperty(default="")
    ui_active_transition_index: bpy.props.IntProperty()

    ui_adding_transition_source_node_name: bpy.props.StringProperty(default="")

    selected_armature: bpy.props.IntProperty(
        name="Armature",
        description="Armature on which the MoVE Network will be previewed.",
        default=-1,
    )

    debug_blend_weight: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    debug_phase: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
