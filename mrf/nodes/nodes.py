import bpy
from .node_tree import NetworkTree
from .node_socket import *
from ..properties import *
from ...cwxml.mrf import *
from ...sollumz_helper import SOLLUMZ_OT_base


# BASE NODE CLASSES
class StateMachineNodeBase(bpy.types.Node):
    """
    Base class for nodes in a state machine transition graph.
    """

    bl_label = "State"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == NetworkTree.bl_idname and ntree.network_tree_type in {"ROOT", "STATE_MACHINE"}

    def add_required_parameters_to_network(self, network):
        pass


class AnimationTreeNodeBase(bpy.types.Node):
    """
    Base class for nodes in an animation tree.
    """

    bl_label = "Node"

    # note: in MRFs these are stored in the parent state of the animation tree, but here makes more sense to store
    #  them in the node itself for editing and previewing purposes
    input_parameters: bpy.props.CollectionProperty(name="Input Parameters", type=ATNodeInputParameter)
    output_parameters: bpy.props.CollectionProperty(name="Output Parameters", type=ATNodeOutputParameter)
    events: bpy.props.CollectionProperty(name="Events", type=ATNodeEvent)
    operations: bpy.props.CollectionProperty(name="Operations", type=ATNodeOperation)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == NetworkTree.bl_idname and ntree.network_tree_type == "ANIMATION_TREE"

    def init_from_xml(self, node_xml):
        raise NotImplementedError

    def add_required_parameters_to_network(self, network):
        for ip in self.input_parameters:
            param_name = ip.source_parameter_name
            data_type = ip.get_parameter_data_type()
            network.network_parameters.try_add(param_name, data_type)
        for op in self.output_parameters:
            param_name = op.target_parameter_name
            data_type = op.get_parameter_data_type()
            network.network_parameters.try_add(param_name, data_type)
        for evt in self.events:
            network.network_parameters.try_add_bool(evt.parameter_name)
        for ops in self.operations:
            for operator in ops.operators:
                if operator.type == "PushParameter":
                    # operations only work on floats
                    network.network_parameters.try_add_float(operator.parameter_name)

    def create_input(self, socket_name, socket_label, socket_type=ATNodeSocket.bl_idname):
        if self.inputs.get(socket_name):
            return None

        input = self.inputs.new(socket_type, socket_name)
        input.text = socket_label
        return input

    def remove_input(self, socket_name):
        input = self.inputs.get(socket_name)
        if input:
            self.inputs.remove(input)

    def create_output(self, socket_name, socket_label, socket_type=ATNodeSocket.bl_idname):
        if self.outputs.get(socket_name):
            return None

        output = self.outputs.new(socket_type, socket_name)
        output.text = socket_label
        return input

    def remove_output(self, socket_name):
        output = self.outputs.get(socket_name)
        if output:
            self.outputs.remove(output)


class ATNodeOutputAnimation(AnimationTreeNodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeOutputAnimation'
    bl_label = 'Output Animation'

    def init(self, context):
        self.create_input("input", "Result")

    def init_from_xml(self, node_xml):
        raise Exception("NodeOutputAnimation cannot be initialized from XML")


# 0 inputs, 1 output
class ATNode0x1(AnimationTreeNodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNode0x1'

    def init(self, context):
        self.create_output("output", "Out")


# 1 input, 1 output
class ATNode1x1(AnimationTreeNodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNode1x1'

    def init(self, context):
        self.create_output("output", "Out")
        self.create_input("input", "In")


# 2 inputs, 1 output
class ATNode2x1(AnimationTreeNodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNode2x1'

    def init(self, context):
        self.create_output("output", "Out")
        self.create_input("input0", "A")
        self.create_input("input1", "B")


# N inputs, 1 output
class ATNodeNx1(AnimationTreeNodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeNx1'

    def init(self, context):
        self.create_output("output", "Out")
        # even though .mrf uses 6 bits to store the children count, some game code arrays are hardcoded to 8
        for i in range(8):
            self.create_input(f"input{i}", f"In {i+1}", socket_type=ATNodeNSocket.bl_idname).hide = True


# ANIMATION TREE NODES


class ATNodeStateMachine(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeStateMachine'
    bl_label = 'State Machine'

    state_machine_tree: bpy.props.PointerProperty(name="State Machine", type=NetworkTree)

    def init_from_xml(self, node_xml: MoveNodeStateMachine):
        pass

    def draw_buttons(self, context, layout):
        if self.state_machine_tree:
            prop = layout.operator(SOLLUMZ_OT_MOVE_NETWORK_open_state_machine.bl_idname)
            prop.state_machine_tree_name = self.state_machine_tree.name


class ATNodeTail(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeTail'
    bl_label = 'Tail'

    def init_from_xml(self, node_xml: MoveNodeTail):
        pass


class ATNodeInlinedStateMachine(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeInlinedStateMachine'
    bl_label = 'Inlined State Machine'

    fallback_animation_tree: bpy.props.PointerProperty(name="Fallback Animation Tree", type=NetworkTree)
    state_machine_tree: bpy.props.PointerProperty(name="State Machine", type=NetworkTree)

    def init_from_xml(self, node_xml: MoveNodeInlinedStateMachine):
        pass

    def draw_buttons(self, context, layout):
        if self.fallback_animation_tree:
            props = layout.operator(SOLLUMZ_OT_MOVE_NETWORK_open_animation_tree.bl_idname)
            props.animation_tree_name = self.fallback_animation_tree.name
        if self.state_machine_tree:
            props = layout.operator(SOLLUMZ_OT_MOVE_NETWORK_open_state_machine.bl_idname)
            props.state_machine_tree_name = self.state_machine_tree.name


class ATNodeBlend(ATNode2x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeBlend'
    bl_label = 'Blend'

    child0_influence_override: InfluenceOverrideProperty(name="Influence Override A")
    child1_influence_override: InfluenceOverrideProperty(name="Influence Override B")
    weight: bpy.props.PointerProperty(name='Weight', type=ParameterizedFloatProperty)
    frame_filter: bpy.props.PointerProperty(name='Frame Filter', type=ParameterizedAssetProperty)
    synchronizer_type: SynchronizerTypeProperty(name="Synchronizer Type")
    synchronizer_tag_flags: bpy.props.StringProperty(name="Synchronizer Tag Flags", default="")
    merge_blend: bpy.props.BoolProperty(name="Merge Blend", default=False)
    unk_flag6: bpy.props.BoolProperty(name="Unk Flag 6", default=False)
    unk_flag7: bpy.props.IntProperty(name="Unk Flag 7", default=0)
    unk_flag21: bpy.props.IntProperty(name="Unk Flag 21", default=0)
    unk_flag23: bpy.props.IntProperty(name="Unk Flag 23", default=0)
    unk_flag25: bpy.props.IntProperty(name="Unk Flag 25", default=0)

    def init_from_xml(self, node_xml: MoveNodeBlend):
        self.child0_influence_override = node_xml.child0_influence_override
        self.child1_influence_override = node_xml.child1_influence_override
        self.weight.set(node_xml.weight)
        self.frame_filter.set(node_xml.frame_filter)
        self.synchronizer_type = node_xml.synchronizer_type or "None"
        self.synchronizer_tag_flags = node_xml.synchronizer_tag_flags
        self.unk_flag6 = node_xml.unk_flag6
        self.unk_flag7 = node_xml.unk_flag7
        self.unk_flag21 = node_xml.unk_flag21
        self.unk_flag23 = node_xml.unk_flag23
        self.unk_flag25 = node_xml.unk_flag25

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.weight)
        network.try_add_parameter(self.frame_filter)

    def draw_buttons(self, context, layout):
        layout.prop(self, "child0_influence_override")
        layout.prop(self, "child1_influence_override")
        self.weight.draw("Weight", context, layout)
        self.frame_filter.draw("Frame Filter", context, layout)
        layout.prop(self, "synchronizer_type")
        if self.synchronizer_type == "Tag":
            layout.prop(self, "synchronizer_tag_flags")
        layout.prop(self, "merge_blend")
        layout.prop(self, "unk_flag6")
        layout.prop(self, "unk_flag7")
        layout.prop(self, "unk_flag21")
        layout.prop(self, "unk_flag23")
        layout.prop(self, "unk_flag25")


class ATNodeAddSubtract(ATNode2x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeAddSubtract'
    bl_label = 'Add-Subtract'

    weight: bpy.props.PointerProperty(name='Weight', type=ParameterizedFloatProperty)
    frame_filter: bpy.props.PointerProperty(name='Frame Filter', type=ParameterizedAssetProperty)

    def init_from_xml(self, node_xml: MoveNodeAddSubtract):
        self.weight.set(node_xml.weight)
        self.frame_filter.set(node_xml.frame_filter)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.weight)
        network.try_add_parameter(self.frame_filter)

    def draw_buttons(self, context, layout):
        self.weight.draw("Weight", context, layout)
        self.frame_filter.draw("Frame Filter", context, layout)


class ATNodeFilter(ATNode1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeFilter'
    bl_label = 'Filter'

    frame_filter: bpy.props.PointerProperty(name='Frame Filter', type=ParameterizedAssetProperty)

    def init_from_xml(self, node_xml: MoveNodeFilter):
        self.frame_filter.set(node_xml.frame_filter)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.frame_filter)

    def draw_buttons(self, context, layout):
        self.frame_filter.draw("Frame Filter", context, layout)


class ATNodeMirror(ATNode1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeMirror'
    bl_label = 'Mirror'

    frame_filter: bpy.props.PointerProperty(name='Frame Filter', type=ParameterizedAssetProperty)

    def init_from_xml(self, node_xml: MoveNodeMirror):
        self.frame_filter.set(node_xml.frame_filter)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.frame_filter)

    def draw_buttons(self, context, layout):
        self.frame_filter.draw("Frame Filter", context, layout)


class ATNodeFrame(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeFrame'
    bl_label = 'Frame'

    frame: bpy.props.StringProperty(name='Frame', default='')

    def init_from_xml(self, node_xml: MoveNodeFrame):
        self.frame = node_xml.frame.parameter

    def draw_buttons(self, context, layout):
        layout.prop(self, "frame")


class ATNodeIk(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeIk'
    bl_label = 'IK'

    def init_from_xml(self, node_xml: MoveNodeIk):
        pass


class ATNodeBlendN(ATNodeNx1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeBlendN'
    bl_label = 'Blend N'

    frame_filter: bpy.props.PointerProperty(name='Frame Filter', type=ParameterizedAssetProperty)
    synchronizer_type: SynchronizerTypeProperty(name="Synchronizer Type")
    synchronizer_tag_flags: bpy.props.StringProperty(name="Synchronizer Tag Flags", default="")
    zero_destination: bpy.props.BoolProperty(name="Zero Destination", default=False)

    def init_from_xml(self, node_xml: MoveNodeBlendN):
        self.frame_filter.set(node_xml.frame_filter)
        self.synchronizer_type = node_xml.synchronizer_type or "None"
        self.synchronizer_tag_flags = node_xml.synchronizer_tag_flags
        self.zero_destination = node_xml.zero_destination
        for i, c in enumerate(node_xml.children):
            self.inputs[f"input{i}"].set(c)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.frame_filter)

    def draw_buttons(self, context, layout):
        self.frame_filter.draw("Frame Filter", context, layout)
        layout.prop(self, "synchronizer_type")
        if self.synchronizer_type == "Tag":
            layout.prop(self, "synchronizer_tag_flags")
        layout.prop(self, "zero_destination")


class ATNodeClip(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeClip'
    bl_label = 'Clip'

    clip: bpy.props.PointerProperty(name='Clip', type=ParameterizedClipProperty)
    phase: bpy.props.PointerProperty(name='Phase', type=ParameterizedFloatProperty)
    rate: bpy.props.PointerProperty(name='Rate', type=ParameterizedFloatProperty)
    delta: bpy.props.PointerProperty(name='Delta', type=ParameterizedFloatProperty)
    looped: bpy.props.PointerProperty(name='Looped', type=ParameterizedBoolProperty)

    def init_from_xml(self, node_xml: MoveNodeClip):
        self.clip.set(node_xml.clip)
        self.phase.set(node_xml.phase)
        self.rate.set(node_xml.rate)
        self.delta.set(node_xml.delta)
        self.looped.set(node_xml.looped)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.clip)
        network.try_add_parameter(self.phase)
        network.try_add_parameter(self.rate)
        network.try_add_parameter(self.delta)
        network.try_add_parameter(self.looped)

    def draw_buttons(self, context, layout):
        self.clip.draw("Clip", context, layout)
        self.phase.draw("Phase", context, layout)
        self.rate.draw("Rate", context, layout)
        self.delta.draw("Delta", context, layout)
        self.looped.draw("Looped", context, layout)
        # self.unk_flag10


class ATNodeExtrapolate(ATNode1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeExtrapolate'
    bl_label = 'Extrapolate'

    damping: bpy.props.PointerProperty(name='Damping', type=ParameterizedFloatProperty)

    def init_from_xml(self, node_xml: MoveNodeExtrapolate):
        self.damping.set(node_xml.damping)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.damping)

    def draw_buttons(self, context, layout):
        self.damping.draw("Damping", context, layout)


class ATNodeExpression(ATNode1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeExpression'
    bl_label = 'Expression'

    weight: bpy.props.PointerProperty(name='Weight', type=ParameterizedFloatProperty)
    expression: bpy.props.PointerProperty(name='Expression', type=ParameterizedAssetProperty)

    def init_from_xml(self, node_xml: MoveNodeExpression):
        self.weight.set(node_xml.weight)
        self.expression.set(node_xml.expression)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.weight)
        network.try_add_parameter(self.expression)

    def draw_buttons(self, context, layout):
        self.weight.draw("Weight", context, layout)
        self.expression.draw("Expression", context, layout)


class ATNodeCapture(ATNode1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeCapture'
    bl_label = 'Capture'

    frame: bpy.props.StringProperty(name='Frame', default='')

    def init_from_xml(self, node_xml: MoveNodeCapture):
        self.frame = node_xml.frame.parameter

    def draw_buttons(self, context, layout):
        layout.prop(self, "frame")


class ATNodeProxy(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeProxy'
    bl_label = 'Proxy'

    node_parameter_name: bpy.props.StringProperty(name='Node Parameter', default='')

    def init_from_xml(self, node_xml: MoveNodeProxy):
        self.node_parameter_name = node_xml.node_parameter_name

    def draw_buttons(self, context, layout):
        layout.prop(self, "node_parameter_name")


class ATNodeAddN(ATNodeNx1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeAddN'
    bl_label = 'Add N'

    frame_filter: bpy.props.PointerProperty(name='Frame Filter', type=ParameterizedAssetProperty)
    synchronizer_type: SynchronizerTypeProperty(name="Synchronizer Type")
    synchronizer_tag_flags: bpy.props.StringProperty(name="Synchronizer Tag Flags", default="")
    zero_destination: bpy.props.BoolProperty(name="Zero Destination", default=False)

    def init_from_xml(self, node_xml: MoveNodeAddN):
        self.frame_filter.set(node_xml.frame_filter)
        self.synchronizer_type = node_xml.synchronizer_type or "None"
        self.synchronizer_tag_flags = node_xml.synchronizer_tag_flags
        self.zero_destination = node_xml.zero_destination
        for i, c in enumerate(node_xml.children):
            self.inputs[f"input{i}"].set(c)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.frame_filter)

    def draw_buttons(self, context, layout):
        self.frame_filter.draw("Frame Filter", context, layout)
        layout.prop(self, "synchronizer_type")
        if self.synchronizer_type == "Tag":
            layout.prop(self, "synchronizer_tag_flags")
        layout.prop(self, "zero_destination")


class ATNodeIdentity(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeIdentity'
    bl_label = 'Identity'

    def init_from_xml(self, node_xml: MoveNodeIdentity):
        pass


class ATNodeMerge(ATNode2x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeMerge'
    bl_label = 'Merge'

    def init_from_xml(self, node_xml: MoveNodeMerge):
        pass


class ATNodePose(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodePose'
    bl_label = 'Pose'

    def init_from_xml(self, node_xml: MoveNodePose):
        pass


class ATNodeMergeN(ATNodeNx1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeMergeN'
    bl_label = 'Merge N'

    frame_filter: bpy.props.PointerProperty(name='Frame Filter', type=ParameterizedAssetProperty)
    synchronizer_type: SynchronizerTypeProperty(name="Synchronizer Type")
    synchronizer_tag_flags: bpy.props.StringProperty(name="Synchronizer Tag Flags", default="")
    zero_destination: bpy.props.BoolProperty(name="Zero Destination", default=False)

    def init_from_xml(self, node_xml: MoveNodeMergeN):
        self.frame_filter.set(node_xml.frame_filter)
        self.synchronizer_type = node_xml.synchronizer_type or "None"
        self.synchronizer_tag_flags = node_xml.synchronizer_tag_flags
        self.zero_destination = node_xml.zero_destination
        for i, c in enumerate(node_xml.children):
            self.inputs[f"input{i}"].set(c)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        network.try_add_parameter(self.frame_filter)

    def draw_buttons(self, context, layout):
        self.frame_filter.draw("Frame Filter", context, layout)
        layout.prop(self, "synchronizer_type")
        if self.synchronizer_type == "Tag":
            layout.prop(self, "synchronizer_tag_flags")
        layout.prop(self, "zero_destination")


class ATNodeInvalid(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeInvalid'
    bl_label = 'Invalid'

    def init_from_xml(self, node_xml: MoveNodeInvalid):
        pass


class ATNodeJointLimit(ATNode1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeJointLimit'
    bl_label = 'Joint Limit'

    def init_from_xml(self, node_xml: MoveNodeJointLimit):
        pass


class ATNodeSubNetwork(ATNode0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeSubNetwork'
    bl_label = 'Sub-Network'

    def init_from_xml(self, node_xml: MoveNodeSubNetwork):
        pass


class SOLLUMZ_OT_MOVE_NETWORK_open_animation_tree(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_open_animation_tree"
    bl_label = "Edit Animation Tree"
    bl_action = bl_label

    animation_tree_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "NODE_EDITOR" and
                context.space_data.tree_type == NetworkTree.bl_idname and
                context.space_data.edit_tree is not None and
                context.space_data.edit_tree.bl_idname == NetworkTree.bl_idname)

    def run(self, context):
        space = context.space_data
        tree = bpy.data.node_groups[self.animation_tree_name]
        if tree:
            space.path.append(tree)


class SOLLUMZ_OT_MOVE_NETWORK_open_state_machine(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_open_state_machine"
    bl_label = "Edit State Machine"
    bl_action = bl_label

    state_machine_tree_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "NODE_EDITOR" and
                context.space_data.tree_type == NetworkTree.bl_idname and
                context.space_data.edit_tree is not None and
                context.space_data.edit_tree.bl_idname == NetworkTree.bl_idname)

    def run(self, context):
        space = context.space_data
        tree = bpy.data.node_groups[self.state_machine_tree_name]
        if tree:
            space.path.append(tree)

# STATE MACHINE TRANSITION GRAPH NODES


class SMNodeStart(StateMachineNodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_SMNodeStart'
    bl_label = 'Start'

    start_state: bpy.props.StringProperty(name="Start State", default="")

    def init(self, context):
        self.hide = True

    def set_start_state(self, state):
        self.start_state = state.name


class SMNodeStateBase(StateMachineNodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_SMNodeStateBase'

    transitions: bpy.props.CollectionProperty(name="Transitions", type=SMTransitionProperties)
    ui_active_transition_index: bpy.props.IntProperty()

    def init(self, context):
        pass

    def add_transition(self, target_state, transition_xml: MoveStateTransition):
        t = self.transitions.add()
        t.target_state = target_state.name
        t.set(transition_xml)

    def add_required_parameters_to_network(self, network):
        super().add_required_parameters_to_network(network)
        for t in self.transitions:
            if t.duration_parameter_name != "":
                network.network_parameters.try_add_float(t.duration_parameter_name)
            if t.progress_parameter_name != "":
                network.network_parameters.try_add_float(t.progress_parameter_name)
            network.try_add_parameter(t.frame_filter)
            for c in t.conditions:
                if c.type in {"ParameterInsideRange", "ParameterOutsideRange",
                              "ParameterGreaterThan", "ParameterGreaterOrEqual",
                              "ParameterLessThan", "ParameterLessOrEqual"}:
                    network.network_parameters.try_add_float(c.parameter)
                elif c.type in {"EventOccurred", "BoolParameterExists", "BoolParameterEquals"}:
                    network.network_parameters.try_add_bool(c.parameter)

    def draw_buttons(self, context, layout):
        # layout.template_list("UI_UL_list", "Transitions", self, "transitions", self, "ui_active_transition_index")
        layout.context_pointer_set("node", self)
        layout.operator("sollumz.move_network_editor_state_add_transition")
        layout.operator("sollumz.move_network_editor_state_connect_transition")


class SMNodeState(SMNodeStateBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_SMNodeState'
    bl_label = 'State'

    animation_tree: bpy.props.PointerProperty(name="Animation Tree", type=NetworkTree)

    def init(self, context):
        pass

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        if self.animation_tree:
            props = layout.operator(SOLLUMZ_OT_MOVE_NETWORK_open_animation_tree.bl_idname)
            props.animation_tree_name = self.animation_tree.name


class SMNodeStateMachine(SMNodeStateBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_SMNodeStateMachine'
    bl_label = 'State Machine'

    state_machine_tree: bpy.props.PointerProperty(name="State Machine", type=NetworkTree)

    def init(self, context):
        pass

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)
        if self.state_machine_tree:
            props = layout.operator(SOLLUMZ_OT_MOVE_NETWORK_open_state_machine.bl_idname)
            props.state_machine_tree_name = self.state_machine_tree.name


classes = [
    ATNodeOutputAnimation,
    ATNodeStateMachine,
    ATNodeTail,
    ATNodeInlinedStateMachine,
    ATNodeBlend,
    ATNodeAddSubtract,
    ATNodeFilter,
    ATNodeMirror,
    ATNodeFrame,
    ATNodeIk,
    ATNodeBlendN,
    ATNodeClip,
    ATNodeExtrapolate,
    ATNodeExpression,
    ATNodeCapture,
    ATNodeProxy,
    ATNodeAddN,
    ATNodeIdentity,
    ATNodeMerge,
    ATNodePose,
    ATNodeMergeN,
    ATNodeInvalid,
    ATNodeJointLimit,
    ATNodeSubNetwork,

    SMNodeStart,
    SMNodeState,
    SMNodeStateMachine,
]

# import traceback
# import sys
called = False


def register():
    global called
    if called:  # TODO: investigate why register() is getting called twice
        return
    called = True
    # print("nodes register <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    # traceback.print_stack(file=sys.stdout)
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
