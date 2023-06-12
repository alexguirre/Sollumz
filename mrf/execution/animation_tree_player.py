from ..nodes.nodes import *
from .clip_player import ClipPlayer
from .frame_buffer import FrameBuffer


class AnimationTreeContext:
    def __init__(self, network, animation_tree, armature_obj):
        self.network = network
        self.animation_tree = animation_tree
        self.armature_obj = armature_obj
        self.delta_time = 0.0

    def get_parameter(self, parameter_name):
        return self.network.network_parameters.get(parameter_name)

    def set_parameter(self, parameter_name, value):
        self.network.network_parameters.set(parameter_name, value)


def exec_node_update_clip(node, context: AnimationTreeContext):
    return node.clip_player.update(context.delta_time)


def exec_node_update_child_passthrough(node, context: AnimationTreeContext):
    assert len(node.children) >= 1
    return node.children[0].update(context)


def exec_node_update_blend(node, context: AnimationTreeContext):
    return exec_node_update_child_passthrough(node, context)
    # frame1 = node.children[0].update(context)
    # frame2 = node.children[1].update(context)
    # frame1.blend(frame2, context.network.debug_blend_weight)  # TODO: get blend weight value
    # return frame1


def exec_node_update_identity(node, context: AnimationTreeContext):
    return FrameBuffer(128)


exec_node_update_dict = {
    ATNodeOutputAnimation.bl_idname: None,
    ATNodeStateMachine.bl_idname: exec_node_update_identity,
    ATNodeTail.bl_idname: exec_node_update_identity,
    ATNodeInlinedStateMachine.bl_idname: exec_node_update_identity,
    ATNodeBlend.bl_idname: exec_node_update_blend,
    ATNodeAddSubtract.bl_idname: exec_node_update_child_passthrough,
    ATNodeFilter.bl_idname: exec_node_update_child_passthrough,
    ATNodeMirror.bl_idname: exec_node_update_child_passthrough,
    ATNodeFrame.bl_idname: exec_node_update_identity,
    ATNodeIk.bl_idname: exec_node_update_identity,
    ATNodeBlendN.bl_idname: exec_node_update_child_passthrough,
    ATNodeClip.bl_idname: exec_node_update_clip,
    ATNodeExtrapolate.bl_idname: exec_node_update_child_passthrough,
    ATNodeExpression.bl_idname: exec_node_update_child_passthrough,
    ATNodeCapture.bl_idname: exec_node_update_child_passthrough,
    ATNodeProxy.bl_idname: exec_node_update_identity,
    ATNodeAddN.bl_idname: exec_node_update_child_passthrough,
    ATNodeIdentity.bl_idname: exec_node_update_identity,
    ATNodeMerge.bl_idname: exec_node_update_child_passthrough,
    ATNodePose.bl_idname: exec_node_update_identity,
    ATNodeMergeN.bl_idname: exec_node_update_child_passthrough,
    ATNodeInvalid.bl_idname: exec_node_update_identity,
    ATNodeJointLimit.bl_idname: exec_node_update_child_passthrough,
    ATNodeSubNetwork.bl_idname: exec_node_update_identity,
}


def exec_node_get_parameter_default(node, context: AnimationTreeContext, parameter_id, extra_arg):
    return None
    # raise Exception("Unknown node parameter id: {}".format(parameter_id))


def exec_node_set_parameter_default(node, context: AnimationTreeContext, parameter_id, extra_arg, value):
    pass
    # raise Exception("Unknown node parameter id: {}".format(parameter_id))


def exec_node_get_parameter_clip(node, context: AnimationTreeContext, parameter_id, extra_arg):
    if parameter_id == "CLIP_CLIP":
        return node.clip_player.clip
    elif parameter_id == "CLIP_PHASE":
        return node.clip_player.phase
    elif parameter_id == "CLIP_RATE":
        return node.clip_player.rate
    elif parameter_id == "CLIP_DELTA":
        return node.clip_player.delta
    elif parameter_id == "CLIP_LOOPED":
        return node.clip_player.looped
    else:
        raise Exception("Unknown clip node parameter id: {}".format(parameter_id))


def exec_node_set_parameter_clip(node, context: AnimationTreeContext, parameter_id, extra_arg, value):
    if parameter_id == "CLIP_CLIP":
        node.clip_player.clip = value
    elif parameter_id == "CLIP_PHASE":
        node.clip_player.phase = float(value)
    elif parameter_id == "CLIP_RATE":
        node.clip_player.rate = float(value)
    elif parameter_id == "CLIP_DELTA":
        node.clip_player.delta = float(value)
    elif parameter_id == "CLIP_LOOPED":
        node.clip_player.looped = bool(value)
    else:
        raise Exception("Unknown clip node parameter id: {}".format(parameter_id))


exec_node_getset_parameter_default = (exec_node_get_parameter_default, exec_node_set_parameter_default)

exec_node_getset_parameter_dict = {
    ATNodeOutputAnimation.bl_idname: (None, None),
    ATNodeStateMachine.bl_idname: exec_node_getset_parameter_default,
    ATNodeTail.bl_idname: exec_node_getset_parameter_default,
    ATNodeInlinedStateMachine.bl_idname: exec_node_getset_parameter_default,
    ATNodeBlend.bl_idname: exec_node_getset_parameter_default,
    ATNodeAddSubtract.bl_idname: exec_node_getset_parameter_default,
    ATNodeFilter.bl_idname: exec_node_getset_parameter_default,
    ATNodeMirror.bl_idname: exec_node_getset_parameter_default,
    ATNodeFrame.bl_idname: exec_node_getset_parameter_default,
    ATNodeIk.bl_idname: exec_node_getset_parameter_default,
    ATNodeBlendN.bl_idname: exec_node_getset_parameter_default,
    ATNodeClip.bl_idname: (exec_node_get_parameter_clip, exec_node_set_parameter_clip),
    ATNodeExtrapolate.bl_idname: exec_node_getset_parameter_default,
    ATNodeExpression.bl_idname: exec_node_getset_parameter_default,
    ATNodeCapture.bl_idname: exec_node_getset_parameter_default,
    ATNodeProxy.bl_idname: exec_node_getset_parameter_default,
    ATNodeAddN.bl_idname: exec_node_getset_parameter_default,
    ATNodeIdentity.bl_idname: exec_node_getset_parameter_default,
    ATNodeMerge.bl_idname: exec_node_getset_parameter_default,
    ATNodePose.bl_idname: exec_node_getset_parameter_default,
    ATNodeMergeN.bl_idname: exec_node_getset_parameter_default,
    ATNodeInvalid.bl_idname: exec_node_getset_parameter_default,
    ATNodeJointLimit.bl_idname: exec_node_getset_parameter_default,
    ATNodeSubNetwork.bl_idname: exec_node_getset_parameter_default,
}


def exec_node_init_default(node, context: AnimationTreeContext):
    pass


def exec_node_init_clip(node, context: AnimationTreeContext):
    node.clip_player = ClipPlayer(context.armature_obj)

    clip_prop = node.ui_node.clip
    if clip_prop.type == "LITERAL":
        pass  # TODO: find clip from literal
    elif clip_prop.type == "PARAMETER":
        node.clip_player.clip = context.get_parameter(clip_prop.parameter)

    phase_prop = node.ui_node.phase
    if phase_prop.type == "LITERAL":
        node.clip_player.phase = phase_prop.value
    elif phase_prop.type == "PARAMETER":
        node.clip_player.phase = context.get_parameter(phase_prop.parameter)

    rate_prop = node.ui_node.rate
    if rate_prop.type == "LITERAL":
        node.clip_player.rate = rate_prop.value
    elif rate_prop.type == "PARAMETER":
        node.clip_player.rate = context.get_parameter(rate_prop.parameter)

    delta_prop = node.ui_node.delta
    if delta_prop.type == "LITERAL":
        node.clip_player.delta = delta_prop.value
    elif delta_prop.type == "PARAMETER":
        node.clip_player.delta = context.get_parameter(delta_prop.parameter)

    looped_prop = node.ui_node.looped
    if looped_prop.type == "LITERAL":
        node.clip_player.looped = looped_prop.value
    elif looped_prop.type == "PARAMETER":
        node.clip_player.looped = context.get_parameter(looped_prop.parameter)


exec_node_init_dict = {
    ATNodeOutputAnimation.bl_idname: None,
    ATNodeStateMachine.bl_idname: exec_node_init_default,
    ATNodeTail.bl_idname: exec_node_init_default,
    ATNodeInlinedStateMachine.bl_idname: exec_node_init_default,
    ATNodeBlend.bl_idname: exec_node_init_default,
    ATNodeAddSubtract.bl_idname: exec_node_init_default,
    ATNodeFilter.bl_idname: exec_node_init_default,
    ATNodeMirror.bl_idname: exec_node_init_default,
    ATNodeFrame.bl_idname: exec_node_init_default,
    ATNodeIk.bl_idname: exec_node_init_default,
    ATNodeBlendN.bl_idname: exec_node_init_default,
    ATNodeClip.bl_idname: exec_node_init_clip,
    ATNodeExtrapolate.bl_idname: exec_node_init_default,
    ATNodeExpression.bl_idname: exec_node_init_default,
    ATNodeCapture.bl_idname: exec_node_init_default,
    ATNodeProxy.bl_idname: exec_node_init_default,
    ATNodeAddN.bl_idname: exec_node_init_default,
    ATNodeIdentity.bl_idname: exec_node_init_default,
    ATNodeMerge.bl_idname: exec_node_init_default,
    ATNodePose.bl_idname: exec_node_init_default,
    ATNodeMergeN.bl_idname: exec_node_init_default,
    ATNodeInvalid.bl_idname: exec_node_init_default,
    ATNodeJointLimit.bl_idname: exec_node_init_default,
    ATNodeSubNetwork.bl_idname: exec_node_init_default,
}


class ATExecNode:
    def __init__(self, ui_node):
        self.ui_node = ui_node
        self.children = []
        self.exec_node_init = exec_node_init_dict[ui_node.bl_idname]
        self.exec_node_update = exec_node_update_dict[ui_node.bl_idname]
        getset_parameter = exec_node_getset_parameter_dict[ui_node.bl_idname]
        self.exec_node_get_parameter = getset_parameter[0]
        self.exec_node_set_parameter = getset_parameter[1]

    def init(self, context: AnimationTreeContext):
        self.exec_node_init(self, context)
        for child in self.children:
            child.init(context)

    def update(self, context: AnimationTreeContext):
        self._pre_update(context)
        result = self.exec_node_update(self, context)
        self._post_update(context)
        return result

    def _pre_update(self, context: AnimationTreeContext):
        """
        Called before the node is updated. Handles:
         - input parameters
         - operations
        """
        for ip in self.ui_node.input_parameters:
            value = context.get_parameter(ip.source_parameter_name)
            self.exec_node_set_parameter(self, context,
                                         ip.target_node_parameter_id, ip.target_node_parameter_extra_arg, value)

    def _post_update(self, context: AnimationTreeContext):
        """
        Called after the node is updated. Handles:
         - output parameters
         - events
        """
        for op in self.ui_node.output_parameters:
            value = self.exec_node_get_parameter(self, context,
                                                 op.source_node_parameter_id, op.source_node_parameter_extra_arg)
            context.set_parameter(op.target_parameter_name, value)

    def __str__(self):
        import textwrap
        s = "{} ({}){}".format(self.ui_node.bl_label, self.ui_node.name, "\n" if len(self.children) > 0 else "")
        for child in self.children:
            s += textwrap.indent("{}{}".format(child, "\n" if child != self.children[-1] else ""), "  ")
        return s


def build_animation_tree_for_execution(animation_tree):
    assert animation_tree.network_tree_type == "ANIMATION_TREE"

    ui_node_to_exec_node = {}
    for link in animation_tree.links:
        ui_from_node = link.from_socket.node
        ui_to_node = link.to_socket.node

        from_node = ui_node_to_exec_node.get(ui_from_node, None)
        if from_node is None:
            from_node = ATExecNode(ui_from_node)
            ui_node_to_exec_node[ui_from_node] = from_node
        to_node = ui_node_to_exec_node.get(ui_to_node, None)
        if to_node is None:
            to_node = ATExecNode(ui_to_node)
            ui_node_to_exec_node[ui_to_node] = to_node

        to_node.children.append(from_node)

    output_node = None
    for ui_node, node in ui_node_to_exec_node.items():
        if ui_node.bl_idname != ATNodeOutputAnimation.bl_idname:
            continue

        output_node = node
        break

    assert output_node is not None, "ATNodeOutputAnimation is required in animation trees"
    assert len(output_node.children) == 1, "ATNodeOutputAnimation must be connected to a node"

    print(str(output_node.children[0]))
    return output_node.children[0]


class AnimationTreePlayer:
    def __init__(self, animation_tree, armature_obj):
        assert animation_tree.network_tree_type == "ANIMATION_TREE"

        self.animation_tree = animation_tree
        self.root_node = build_animation_tree_for_execution(animation_tree)
        self.initialized = False
        self.context = AnimationTreeContext(animation_tree.network_root, animation_tree, armature_obj)

    def init(self):
        self.root_node.init(self.context)
        self.initialized = True

    def update(self, delta_time):
        if not self.initialized:
            self.init()

        self.context.delta_time = delta_time
        return self.root_node.update(self.context)
