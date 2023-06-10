import bpy
from ..properties import *

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
    debug_rate: bpy.props.FloatProperty(default=1.0, min=0.0, max=5.0)

    network_parameters: bpy.props.PointerProperty(type=NetworkParameters)
    ui_network_param_float_new_name: bpy.props.StringProperty(name="New float MoVE Network parameter...", default="")
    ui_network_param_bool_new_name: bpy.props.StringProperty(name="New bool MoVE Network parameter...", default="")
    ui_network_param_clip_new_name: bpy.props.StringProperty(name="New clip MoVE Network parameter...", default="")
    ui_network_param_asset_new_name: bpy.props.StringProperty(name="New asset MoVE Network parameter...", default="")

    def try_add_parameter(self, parameterized_value):
        # print("try_add_parameter %s" % parameterized_value.parameter)
        if parameterized_value.type != "PARAMETER":
            return

        if isinstance(parameterized_value, ParameterizedFloatProperty):
            self.network_parameters.try_add_float(parameterized_value.parameter)
        elif isinstance(parameterized_value, ParameterizedBoolProperty):
            self.network_parameters.try_add_bool(parameterized_value.parameter)
        elif isinstance(parameterized_value, ParameterizedClipProperty):
            self.network_parameters.try_add_clip(parameterized_value.parameter)
        elif isinstance(parameterized_value, ParameterizedAssetProperty):
            self.network_parameters.try_add_asset(parameterized_value.parameter)
        else:
            raise Exception("Unknown parameterized value type.")
