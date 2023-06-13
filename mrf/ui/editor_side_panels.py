import bpy
from ..nodes.node_tree import NetworkTree
from ..nodes.nodes import ATNodeOutputAnimation
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
            r = layout.row(align=True)
            r.prop(node_tree, param_name_prop, text="")
            props = r.operator(add_network_parameter_op, text="", icon="ADD")
            props.parameter_name_prop = param_name_prop
            props.parameter_name = getattr(node_tree, param_name_prop)
            props.parameter_type = param_type

        b = self.layout.box()
        b.label(text="Parameters", icon="SETTINGS")
        b.label(text="Floats")
        for param in node_tree.network_parameters.parameters_float:
            r = b.row(align=True)
            r.prop(param, "value", text=param.name)
            r.operator(delete_network_parameter_op, text="", icon="X").parameter_name = param.name
        draw_add_network_parameter(b, "ui_network_param_float_new_name", "float")
        b.separator()
        b.label(text="Bools")
        for param in node_tree.network_parameters.parameters_bool:
            r = b.row(align=True)
            r.prop(param, "value", text=param.name)
            r.operator(delete_network_parameter_op, text="", icon="X").parameter_name = param.name
        draw_add_network_parameter(b, "ui_network_param_bool_new_name", "bool")
        b.separator()
        b.label(text="Clips")
        for param in node_tree.network_parameters.parameters_clip:
            r = b.row(align=True)
            r.prop(param, "clip_dictionary", text=param.name)
            r.prop(param, "clip", text="")
            r.operator(delete_network_parameter_op, text="", icon="X").parameter_name = param.name
        draw_add_network_parameter(b, "ui_network_param_clip_new_name", "clip")
        b.separator()
        b.label(text="Assets")
        for param in node_tree.network_parameters.parameters_asset:
            r = b.row(align=True)
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
        item.draw(context, layout)


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
        transition.frame_filter.draw("Frame Filter", context, self.layout)
        self.layout.prop(transition, "unk_flag2_detach_update_observers")
        self.layout.prop(transition, "unk_flag18")
        self.layout.prop(transition, "unk_flag19")
        self.layout.label(text="Conditions:")
        self.layout.template_list(SOLLUMZ_UL_MOVE_NETWORK_SMConditionsList.bl_idname, "conditions",
                                  transition, "conditions", transition, "ui_active_condition_index")


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


class ATNodeActionsPanel(bpy.types.Panel):
    bl_label = "Actions"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_ATNodeActionsPanel"
    bl_category = "Node"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == 'ANIMATION_TREE' and
                context.active_node is not None and
                context.active_node.bl_idname != ATNodeOutputAnimation.bl_idname)

    def draw(self, context):
        pass


class ATNodeActionsSubPanel:
    bl_category = ATNodeActionsPanel.bl_category
    bl_space_type = ATNodeActionsPanel.bl_space_type
    bl_region_type = ATNodeActionsPanel.bl_region_type
    bl_parent_id = ATNodeActionsPanel.bl_idname

    def draw(self, context):
        node_tree = context.space_data.edit_tree
        network = node_tree.network_root or node_tree
        node = context.active_node

        def draw_parameter_name_prop(layout, obj, prop_name, data_type, text=None):
            layout.prop_search(obj, prop_name, network.network_parameters, "parameters_{}".format(data_type), text=text)

        self.do_draw(context, node, draw_parameter_name_prop)

    def do_draw(self, context, node, draw_parameter_name_prop):
        raise NotImplementedError


class ATNodeActionsInputParametersPanel(ATNodeActionsSubPanel, bpy.types.Panel):
    bl_label = "Input Parameters"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_ATNodeActionsInputParametersPanel"
    bl_order = 0

    def do_draw(self, context, node, draw_parameter_name_prop):
        for ip in node.input_parameters:
            draw_parameter_name_prop(self.layout, ip, "source_parameter_name", ip.get_parameter_data_type())
            self.layout.prop(ip, "target_node_parameter_id")
            self.layout.prop(ip, "target_node_parameter_extra_arg")


class ATNodeActionsOutputParametersPanel(ATNodeActionsSubPanel, bpy.types.Panel):
    bl_label = "Output Parameters"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_ATNodeActionsOutputParametersPanel"
    bl_order = 1

    def do_draw(self, context, node, draw_parameter_name_prop):
        for op in node.output_parameters:
            draw_parameter_name_prop(self.layout, op, "target_parameter_name", op.get_parameter_data_type())
            self.layout.prop(op, "source_node_parameter_id")
            self.layout.prop(op, "source_node_parameter_extra_arg")


class ATNodeActionsEventsPanel(ATNodeActionsSubPanel, bpy.types.Panel):
    bl_label = "Events"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_ATNodeActionsEventsPanel"
    bl_order = 2

    def do_draw(self, context, node, draw_parameter_name_prop):
        for evt in node.events:
            self.layout.prop(evt, "node_event_id")
            draw_parameter_name_prop(self.layout, evt, "parameter_name", "bool")


class ATNodeActionsOperationsPanel(ATNodeActionsSubPanel, bpy.types.Panel):
    bl_label = "Operations"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_ATNodeActionsOperationsPanel"
    bl_order = 3

    def do_draw(self, context, node, draw_parameter_name_prop):
        for ops in node.operations:
            self.layout.prop(ops, "node_parameter_id")
            self.layout.prop(ops, "node_parameter_extra_arg")
            b = self.layout.box()
            b.label(text="Operators")
            for operator in ops.operators:
                operator.draw(context, b, draw_parameter_name_prop)
