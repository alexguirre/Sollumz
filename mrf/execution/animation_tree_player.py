import bl_math
from ..nodes.nodes import *
from ..properties import ATNodeOperation
from .clip_player import ClipPlayer
from .frame_buffer import FrameBuffer


class AnimationTreeContext:
    def __init__(self, network, animation_tree, armature_obj):
        self.network = network
        self.animation_tree = animation_tree
        self.armature_obj = armature_obj
        self.num_bones = len(self.armature_obj.pose.bones)
        self.delta_time = 0.0

    def get_parameter(self, parameter_name):
        return self.network.network_parameters.get(parameter_name)

    def set_parameter(self, parameter_name, value):
        self.network.network_parameters.set(parameter_name, value)


def evaluate_operation(ops: ATNodeOperation, context: AnimationTreeContext):
    # print("--------------------------------")
    stack = [0.0] * len(ops.operators)  # TODO: cache stacks?
    stack_top = -1
    for operator in ops.operators:
        if operator.type == "PushLiteral":
            stack_top += 1
            stack[stack_top] = operator.value
            # print(f"PushLiteral {operator.value}")
        elif operator.type == "PushParameter":
            stack_top += 1
            stack[stack_top] = float(context.get_parameter(operator.parameter_name))
            # print(f"PushParameter {operator.parameter_name}  ({stack[stack_top]})")
        elif operator.type == "Add":
            stack[stack_top - 1] += stack[stack_top]
            stack_top -= 1
            # print(f"+ ({stack[stack_top]})")
        elif operator.type == "Multiply":
            stack[stack_top - 1] *= stack[stack_top]
            stack_top -= 1
            # print(f"* ({stack[stack_top]})")
        elif operator.type == "Remap":
            v = stack[stack_top]
            v_min = operator.min
            v_max = operator.max
            v_range_length = v_max - v_min
            v = bl_math.clamp(v, v_min, v_max)
            if v_range_length != 0.0:
                # convert to 0.0-1.0 range
                v = (v - v_min) / v_range_length
            for r in operator.remap_ranges:
                if v <= r.percent:
                    # remap to new range
                    v = r.min + r.length * v
                    break
            # print(f"remap {stack[stack_top]} -> {v}")
            stack[stack_top] = v
    # print(f"RESULT = {stack[stack_top]}")
    # print("--------------------------------")
    return stack[stack_top]


def exec_node_update_clip(node, context: AnimationTreeContext):
    return node.clip_player.update(context.delta_time)


def exec_node_update_child_passthrough(node, context: AnimationTreeContext):
    assert len(node.children) >= 1
    return node.children[0].update(context)


def exec_node_update_blend(node, context: AnimationTreeContext):
    frame1 = node.children[0].update(context)
    frame2 = node.children[1].update(context)
    frame1.blend(frame2, node.blend_weight)
    return frame1


def exec_node_update_add_subtract(node, context: AnimationTreeContext):
    frame1 = node.children[0].update(context)
    # frame2 = node.children[1].update(context)
    # frame1.apply_additive(frame2, node.add_weight)
    return frame1


def exec_node_update_blend_n(node, context: AnimationTreeContext):
    num_children = len(node.children)
    if num_children == 0:
        return FrameBuffer(context.num_bones)
    elif num_children == 1:
        return node.children[0].update(context)

    # normalize and calculate weights such that we can blend in pairs
    # weights are stored in reversed order and the last weight can be ignored
    #  0-1 -> weights[-2], 1-2 -> weights[-3], 2-3 -> weights[-4]...
    weights = node.blend_n_weights.copy()
    weights_total = min(sum(weights), 1.0)
    weights_accumulator = 1.0 - weights_total if weights_total < 1.0 else 0.0

    for i in reversed(range(len(weights))):
        w = weights[i]
        weights_accumulator += w
        if weights_accumulator < 0.001:
            weights[i] = 1.0
            weights_accumulator = 0.0
        else:
            weight_normalized = w / weights_accumulator
            weight_normalized = bl_math.clamp(weight_normalized, 0.0, 1.0)
            weights[i] = 1.0 - weight_normalized

    # at_trace("update_blend_n")
    # at_trace(f"  orig weights = {node.blend_n_weights}")
    # at_trace(f"   new weights = {weights}")

    frames = [child.update(context) for child in node.children]

    # blend in pairs, storing results in the second frame, such that the last frame is the final result
    #  0-1, 1-2, 2-3...
    for i in range(len(weights) - 1):
        frames[i + 1].blend(frames[i], weights[-2 - i])

    return frames[-1]


def exec_node_update_merge(node, context: AnimationTreeContext):
    frame1 = node.children[0].update(context)
    frame2 = node.children[1].update(context)
    frame1.merge(frame2)
    return frame1


def exec_node_update_state_machine(node, context: AnimationTreeContext):
    return node.state_machine_player.update(context.delta_time)


def exec_node_update_invalid(node, context: AnimationTreeContext):
    return FrameBuffer(context.num_bones)


def exec_node_update_identity(node, context: AnimationTreeContext):
    f = FrameBuffer(context.num_bones)
    f.make_identity()
    return f


exec_node_update_dict = {
    ATNodeOutputAnimation.bl_idname: None,
    ATNodeStateMachine.bl_idname: exec_node_update_state_machine,
    ATNodeTail.bl_idname: exec_node_update_identity,
    ATNodeInlinedStateMachine.bl_idname: exec_node_update_identity,
    ATNodeBlend.bl_idname: exec_node_update_blend,
    ATNodeAddSubtract.bl_idname: exec_node_update_add_subtract,
    ATNodeFilter.bl_idname: exec_node_update_child_passthrough,
    ATNodeMirror.bl_idname: exec_node_update_child_passthrough,
    ATNodeFrame.bl_idname: exec_node_update_identity,
    ATNodeIk.bl_idname: exec_node_update_identity,
    ATNodeBlendN.bl_idname: exec_node_update_blend_n,
    ATNodeClip.bl_idname: exec_node_update_clip,
    ATNodeExtrapolate.bl_idname: exec_node_update_child_passthrough,
    ATNodeExpression.bl_idname: exec_node_update_child_passthrough,
    ATNodeCapture.bl_idname: exec_node_update_child_passthrough,
    ATNodeProxy.bl_idname: exec_node_update_identity,
    ATNodeAddN.bl_idname: exec_node_update_child_passthrough,
    ATNodeIdentity.bl_idname: exec_node_update_identity,
    ATNodeMerge.bl_idname: exec_node_update_merge,
    ATNodePose.bl_idname: exec_node_update_identity,
    ATNodeMergeN.bl_idname: exec_node_update_child_passthrough,
    ATNodeInvalid.bl_idname: exec_node_update_invalid,
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


def exec_node_get_parameter_blend(node, context: AnimationTreeContext, parameter_id, extra_arg):
    if parameter_id == "BLEND_FILTER":
        return None
    elif parameter_id == "BLEND_WEIGHT":
        return node.blend_weight
    else:
        raise Exception("Unknown blend node parameter id: {}".format(parameter_id))


def exec_node_set_parameter_blend(node, context: AnimationTreeContext, parameter_id, extra_arg, value):
    if parameter_id == "BLEND_FILTER":
        pass
    elif parameter_id == "BLEND_WEIGHT":
        node.blend_weight = float(value)
    else:
        raise Exception("Unknown blend node parameter id: {}".format(parameter_id))


def exec_node_get_parameter_add_subtract(node, context: AnimationTreeContext, parameter_id, extra_arg):
    if parameter_id == "BLEND_FILTER":
        return None
    elif parameter_id == "BLEND_WEIGHT":
        return node.blend_weight
    else:
        raise Exception("Unknown blend node parameter id: {}".format(parameter_id))


def exec_node_set_parameter_add_subtract(node, context: AnimationTreeContext, parameter_id, extra_arg, value):
    if parameter_id == "ADDSUBTRACT_FILTER":
        pass
    elif parameter_id == "ADDSUBTRACT_WEIGHT":
        node.add_weight = float(value)
    else:
        raise Exception("Unknown add-subtract node parameter id: {}".format(parameter_id))


def exec_node_get_parameter_blend_n(node, context: AnimationTreeContext, parameter_id, extra_arg):
    if parameter_id == "BLENDN_FILTER":
        return None
    elif parameter_id == "BLENDN_CHILDWEIGHT":
        return node.blend_n_weights[int(extra_arg)]
    elif parameter_id == "BLENDN_CHILDFILTER":
        return None
    else:
        raise Exception("Unknown blend node parameter id: {}".format(parameter_id))


def exec_node_set_parameter_blend_n(node, context: AnimationTreeContext, parameter_id, extra_arg, value):
    if parameter_id == "BLENDN_FILTER":
        pass
    elif parameter_id == "BLENDN_CHILDWEIGHT":
        node.blend_n_weights[int(extra_arg)] = float(value)
    elif parameter_id == "BLENDN_CHILDFILTER":
        pass
    else:
        raise Exception("Unknown blend node parameter id: {}".format(parameter_id))


def exec_node_get_parameter_merge(node, context: AnimationTreeContext, parameter_id, extra_arg):
    if parameter_id == "MERGE_FILTER":
        return None
    else:
        raise Exception("Unknown merge node parameter id: {}".format(parameter_id))


def exec_node_set_parameter_merge(node, context: AnimationTreeContext, parameter_id, extra_arg, value):
    if parameter_id == "MERGE_FILTER":
        pass
    else:
        raise Exception("Unknown merge node parameter id: {}".format(parameter_id))


exec_node_getset_parameter_default = (exec_node_get_parameter_default, exec_node_set_parameter_default)

exec_node_getset_parameter_dict = {
    ATNodeOutputAnimation.bl_idname: (None, None),
    ATNodeStateMachine.bl_idname: exec_node_getset_parameter_default,
    ATNodeTail.bl_idname: exec_node_getset_parameter_default,
    ATNodeInlinedStateMachine.bl_idname: exec_node_getset_parameter_default,
    ATNodeBlend.bl_idname: (exec_node_get_parameter_blend, exec_node_set_parameter_blend),
    ATNodeAddSubtract.bl_idname: (exec_node_get_parameter_add_subtract, exec_node_set_parameter_add_subtract),
    ATNodeFilter.bl_idname: exec_node_getset_parameter_default,
    ATNodeMirror.bl_idname: exec_node_getset_parameter_default,
    ATNodeFrame.bl_idname: exec_node_getset_parameter_default,
    ATNodeIk.bl_idname: exec_node_getset_parameter_default,
    ATNodeBlendN.bl_idname: (exec_node_get_parameter_blend_n, exec_node_set_parameter_blend_n),
    ATNodeClip.bl_idname: (exec_node_get_parameter_clip, exec_node_set_parameter_clip),
    ATNodeExtrapolate.bl_idname: exec_node_getset_parameter_default,
    ATNodeExpression.bl_idname: exec_node_getset_parameter_default,
    ATNodeCapture.bl_idname: exec_node_getset_parameter_default,
    ATNodeProxy.bl_idname: exec_node_getset_parameter_default,
    ATNodeAddN.bl_idname: exec_node_getset_parameter_default,
    ATNodeIdentity.bl_idname: exec_node_getset_parameter_default,
    ATNodeMerge.bl_idname: (exec_node_get_parameter_merge, exec_node_set_parameter_merge),
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
        if clip_prop.container_type == "ClipDictionary":
            clip_dictionary_obj = bpy.data.objects.get(clip_prop.container_name, None)
            clip_obj = bpy.data.objects.get(clip_prop.name, None)  # TODO: look in clip dictionary instead
            node.clip_player.clip = clip_obj
        else:
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


def exec_node_init_blend(node, context: AnimationTreeContext):
    # node.blend_filter = None
    node.blend_weight = 0.0

    weight_prop = node.ui_node.weight
    if weight_prop.type == "LITERAL":
        node.blend_weight = weight_prop.value
    elif weight_prop.type == "PARAMETER":
        node.blend_weight = context.get_parameter(weight_prop.parameter)


def exec_node_init_add_subtract(node, context: AnimationTreeContext):
    # node.add_filter = None
    node.add_weight = 0.0

    weight_prop = node.ui_node.weight
    if weight_prop.type == "LITERAL":
        node.add_weight = weight_prop.value
    elif weight_prop.type == "PARAMETER":
        node.add_weight = context.get_parameter(weight_prop.parameter)


def exec_node_init_blend_n(node, context: AnimationTreeContext):
    # node.blend_filter = None
    node.blend_n_weights = [0.0] * len(node.children)

    # TODO: blend_n_weights
    # weight_prop = node.ui_node.weight
    # if weight_prop.type == "LITERAL":
    #     node.blend_weight = weight_prop.value
    # elif weight_prop.type == "PARAMETER":
    #     node.blend_weight = context.get_parameter(weight_prop.parameter)


def exec_node_init_merge(node, context: AnimationTreeContext):
    # node.merge_filter = None
    pass


def exec_node_init_state_machine(node, context: AnimationTreeContext):
    from .state_machine_player import StateMachinePlayer
    node.state_machine_player = StateMachinePlayer(node.ui_node.state_machine_tree, context.armature_obj)


exec_node_init_dict = {
    ATNodeOutputAnimation.bl_idname: None,
    ATNodeStateMachine.bl_idname: exec_node_init_state_machine,
    ATNodeTail.bl_idname: exec_node_init_default,
    ATNodeInlinedStateMachine.bl_idname: exec_node_init_default,
    ATNodeBlend.bl_idname: exec_node_init_blend,
    ATNodeAddSubtract.bl_idname: exec_node_init_add_subtract,
    ATNodeFilter.bl_idname: exec_node_init_default,
    ATNodeMirror.bl_idname: exec_node_init_default,
    ATNodeFrame.bl_idname: exec_node_init_default,
    ATNodeIk.bl_idname: exec_node_init_default,
    ATNodeBlendN.bl_idname: exec_node_init_blend_n,
    ATNodeClip.bl_idname: exec_node_init_clip,
    ATNodeExtrapolate.bl_idname: exec_node_init_default,
    ATNodeExpression.bl_idname: exec_node_init_default,
    ATNodeCapture.bl_idname: exec_node_init_default,
    ATNodeProxy.bl_idname: exec_node_init_default,
    ATNodeAddN.bl_idname: exec_node_init_default,
    ATNodeIdentity.bl_idname: exec_node_init_default,
    ATNodeMerge.bl_idname: exec_node_init_merge,
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
        for ops in self.ui_node.operations:
            value = evaluate_operation(ops, context)
            self.exec_node_set_parameter(self, context,
                                         ops.node_parameter_id, ops.node_parameter_extra_arg, value)

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

        to_node.children.append(from_node)  # TODO: verify that the children order is correct

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
