import bpy
from ..nodes.node_tree import NetworkTree
from ...sollumz_ui import SOLLUMZ_UL_armature_list
from ..operators.preview_network import SOLLUMZ_OT_MOVE_NETWORK_preview_network
from ..operators.preview_animation_tree import SOLLUMZ_OT_MOVE_NETWORK_preview_animation_tree
from ..operators.layout_animation_tree import SOLLUMZ_OT_MOVE_NETWORK_layout_animation_tree
from ..operators.delete_network_parameter import SOLLUMZ_OT_MOVE_NETWORK_delete_network_parameter
from ..operators.add_network_parameter import SOLLUMZ_OT_MOVE_NETWORK_add_network_parameter


class NetworkPropertiesPanel(bpy.types.Panel):
    bl_label = "MoVE Network"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_NetworkPropertiesPanel"
    bl_category = "Network"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == NetworkTree.bl_idname and
                context.space_data.edit_tree is not None and
                context.space_data.edit_tree.bl_idname == NetworkTree.bl_idname)

    def draw(self, context):
        node_tree = context.space_data.edit_tree
        if node_tree.network_root is not None:
            node_tree = node_tree.network_root

        self.layout.prop(node_tree, "name")

        self.layout.operator(SOLLUMZ_OT_MOVE_NETWORK_preview_network.bl_idname)

        b = self.layout.box()
        b.label(text="Target skeleton", icon="ARMATURE_DATA")
        b.template_list(SOLLUMZ_UL_armature_list.bl_idname, "",
                        bpy.data, "armatures", node_tree, "selected_armature")

        b = self.layout.box()
        b.label(text="Debug", icon="TOOL_SETTINGS")
        b.prop(node_tree, "debug_blend_weight")
        b.prop(node_tree, "debug_phase")
        b.prop(node_tree, "debug_rate")

        delete_network_parameter_op = SOLLUMZ_OT_MOVE_NETWORK_delete_network_parameter.bl_idname
        add_network_parameter_op = SOLLUMZ_OT_MOVE_NETWORK_add_network_parameter.bl_idname

        def draw_add_network_parameter(layout, param_name_prop, param_type):
            r = layout.row()
            r.prop(node_tree, param_name_prop, text="")
            props = r.operator(add_network_parameter_op, text="", icon="ADD")
            props.parameter_name_prop = param_name_prop
            props.parameter_name = getattr(node_tree, param_name_prop)
            props.parameter_type = param_type

        b = self.layout.box()
        b.label(text="Parameters", icon="SETTINGS")
        b.label(text="Floats")
        for param in node_tree.network_parameters.parameters_float:
            r = b.row()
            r.prop(param, "value", text=param.name)
            r.operator(delete_network_parameter_op, text="", icon="X").parameter_name = param.name
        draw_add_network_parameter(b, "ui_network_param_float_new_name", "float")
        b.separator()
        b.label(text="Bools")
        for param in node_tree.network_parameters.parameters_bool:
            r = b.row()
            r.prop(param, "value", text=param.name)
            r.operator(delete_network_parameter_op, text="", icon="X").parameter_name = param.name
        draw_add_network_parameter(b, "ui_network_param_bool_new_name", "bool")
        b.separator()
        b.label(text="Clips")
        for param in node_tree.network_parameters.parameters_clip:
            r = b.row()
            r.prop(param, "value", text=param.name)
            r.operator(delete_network_parameter_op, text="", icon="X").parameter_name = param.name
        draw_add_network_parameter(b, "ui_network_param_clip_new_name", "clip")
        b.separator()
        b.label(text="Assets")
        for param in node_tree.network_parameters.parameters_asset:
            r = b.row()
            r.prop(param, "value", text=param.name)
            r.operator(delete_network_parameter_op, text="", icon="X").parameter_name = param.name
        draw_add_network_parameter(b, "ui_network_param_asset_new_name", "asset")


class AnimationTreePropertiesPanel(bpy.types.Panel):
    bl_label = "Animation Tree"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_AnimationTreePropertiesPanel"
    bl_category = "Animation Tree"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == 'ANIMATION_TREE')

    def draw(self, context):
        node_tree = context.space_data.edit_tree

        self.layout.prop(node_tree, "name")
        self.layout.operator(SOLLUMZ_OT_MOVE_NETWORK_layout_animation_tree.bl_idname)
        self.layout.operator(SOLLUMZ_OT_MOVE_NETWORK_preview_animation_tree.bl_idname)


class SOLLUMZ_UL_MOVE_NETWORK_SMConditionsList(bpy.types.UIList):
    bl_idname = "SOLLUMZ_UL_MOVE_NETWORK_SMConditionsList"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        item.draw(layout)


class StateMachineActiveTransitionPanel(bpy.types.Panel):
    """
    Panel for editing the active transition properties.
    The active transition is the one clicked by the user (see editor_state_machine_input operator).
    """
    bl_label = "Transition"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_StateMachineActiveTransitionPanel"
    bl_category = "State Machine"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == "STATE_MACHINE" and
                space.edit_tree.ui_active_transition_source_node_name != "")

    def draw(self, context):
        node_tree = context.space_data.edit_tree
        source_node = node_tree.nodes[node_tree.ui_active_transition_source_node_name]
        transition = source_node.transitions[node_tree.ui_active_transition_index]

        self.layout.prop(transition, "target_state")
        self.layout.prop(transition, "duration")
        self.layout.prop(transition, "duration_parameter_name")
        self.layout.prop(transition, "progress_parameter_name")
        self.layout.prop(transition, "blend_modifier")
        self.layout.prop(transition, "synchronizer_type")
        if transition.synchronizer_type == "Tag":
            self.layout.prop(transition, "synchronizer_tag_flags")
        # TODO: disable parameters support for this frame filter
        transition.frame_filter.draw("Frame Filter", self.layout)
        self.layout.prop(transition, "unk_flag2_detach_update_observers")
        self.layout.prop(transition, "unk_flag18")
        self.layout.prop(transition, "unk_flag19")
        self.layout.label(text="Conditions:")
        self.layout.template_list("SOLLUMZ_UL_MOVE_NETWORK_SMConditionsList", "conditions", transition, "conditions", transition, "ui_active_condition_index")


class StateMachinePropertiesPanel(bpy.types.Panel):
    bl_label = "State Machine"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_StateMachinePropertiesPanel"
    bl_category = "State Machine"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == 'STATE_MACHINE')

    def draw(self, context):
        node_tree = context.space_data.edit_tree

        self.layout.prop(node_tree, 'name')
