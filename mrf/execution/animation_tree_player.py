from ..nodes.nodes import *
from .clip_player import ClipPlayer
from .frame_buffer import FrameBuffer


class AnimationTreeContext:
    def __init__(self, network, animation_tree, armature_obj):
        self.network = network
        self.animation_tree = animation_tree
        self.armature_obj = armature_obj
        self.delta_time = 0.0


_tmp_idx = 0
def exec_node_update_clip(node, context: AnimationTreeContext):
    clip_player = getattr(node, "exec_clip_player", None)
    if clip_player is None:
        global _tmp_idx
        clip_obj = bpy.data.objects[("sweep_high_full", "sweep_med_full")[_tmp_idx]]  # TODO: get clip
        _tmp_idx ^= 1
        clip_player = ClipPlayer(clip_obj, context.armature_obj)
        node.exec_clip_player = clip_player

    return clip_player.update(context.delta_time)


def exec_node_update_child_passthrough(node, context: AnimationTreeContext):
    assert len(node.children) >= 1
    return node.children[0].update(context)


def exec_node_update_blend(node, context: AnimationTreeContext):
    frame1 = node.children[0].update(context)
    frame2 = node.children[1].update(context)
    frame1.blend(frame2, context.network.debug_blend_weight)  # TODO: get blend weight value
    return frame1


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


class ATExecNode:
    def __init__(self, ui_node):
        self.ui_node = ui_node
        self.children = []
        self.exec_node_update = exec_node_update_dict[ui_node.bl_idname]

    def update(self, context: AnimationTreeContext):
        return self.exec_node_update(self, context)

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
        self.context = AnimationTreeContext(animation_tree.network_root, animation_tree, armature_obj)

    def update(self, delta_time):
        self.context.delta_time = delta_time
        return self.root_node.update(self.context)
