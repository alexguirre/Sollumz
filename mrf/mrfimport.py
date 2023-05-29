import os

import bpy
from ..cwxml.mrf import *
from ..tools.blenderhelper import create_empty_object
from ..sollumz_properties import SollumType
from .properties import MoveNetworkProperties, MoveNetworkBitProperties
from .ui.node_tree import NodeTree
from .ui.node_socket import NodeSocket
from .ui.nodes import *


def import_mrf(filepath: str):
    mrf_xml = MRF.from_xml_file(filepath)
    MRF.write_xml(mrf_xml, "D:\\re\\gta5\\test.mrf.xml")
    move_network_to_obj(mrf_xml, os.path.basename(filepath.replace(MRF.file_extension, "")))


def move_network_to_obj(mrf_xml: MoveNetwork, name: str):
    # move_network_obj = create_empty_object(SollumType.MOVE_NETWORK, name)
    #
    # set_move_network_properties(mrf_xml, move_network_obj)

    build_node_tree(mrf_xml, name)


# def set_move_network_properties(mrf_xml: MoveNetwork, obj: bpy.types.Object):
#     obj.move_network_properties.test = 1234
#
#     for trigger in mrf_xml.triggers:
#         trigger_props = obj.move_network_properties.triggers.add()
#         trigger_props.name = trigger.name
#         trigger_props.bit_position = trigger.bit_position
#     for flag in mrf_xml.flags:
#         flag_props = obj.move_network_properties.flags.add()
#         flag_props.name = flag.name
#         flag_props.bit_position = flag.bit_position


def build_node_tree(mrf_xml: MoveNetwork, name: str):
    tree: NodeTree = bpy.data.node_groups.new(name, NodeTree.bl_idname)
    build_state_nodes(tree, mrf_xml.root_state)
    layout_node_tree(tree)
    return tree


def build_state_nodes(tree: NodeTree, state, parent_frame=None):
    def _build_state_nodes(s: MoveNodeState):
        state_frame = tree.nodes.new('NodeFrame')
        state_frame.name = s.name
        state_frame.label = s.name
        if parent_frame is not None:
            state_frame.parent = parent_frame
        final_output = tree.nodes.new(NodeOutputAnimation.bl_idname)
        final_output.parent = state_frame
        root_node = create_anim_node_tree(tree, s.initial_node, parent_frame=state_frame)
        tree.links.new(root_node.outputs["output"], final_output.inputs["input"])
        return state_frame

    def _build_state_machine_nodes(sm: MoveNodeStateMachine):
        state_machine_frame = tree.nodes.new('NodeFrame')
        state_machine_frame.name = sm.name
        state_machine_frame.label = sm.name
        if parent_frame is not None:
            state_machine_frame.parent = parent_frame
        for child in sm.states:
            build_state_nodes(tree, child, parent_frame=state_machine_frame)
        return state_machine_frame

    def _build_inlined_state_machine_nodes(sm: MoveNodeStateMachine):
        state_machine_frame = tree.nodes.new('NodeFrame')
        state_machine_frame.name = sm.name
        state_machine_frame.label = sm.name
        if parent_frame is not None:
            state_machine_frame.parent = parent_frame
        for child in sm.states:
            build_state_nodes(tree, child, parent_frame=state_machine_frame)

        state_machine_fallback_frame = tree.nodes.new('NodeFrame')
        state_machine_fallback_frame.name = "%s.Fallback" % sm.name
        state_machine_fallback_frame.label = "%s (Fallback)" % sm.name
        if parent_frame is not None:
            state_machine_fallback_frame.parent = parent_frame
        fallback_final_output = tree.nodes.new(NodeOutputAnimation.bl_idname)
        fallback_final_output.parent = state_machine_fallback_frame
        root_node = create_anim_node_tree(tree, sm.fallback_node, parent_frame=state_machine_fallback_frame)
        tree.links.new(root_node.outputs["output"], fallback_final_output.inputs["input"])
        return state_machine_frame

    if state.type == MoveNodeState.type:
        return _build_state_nodes(state)
    elif state.type == MoveNodeStateMachine.type:
        return _build_state_machine_nodes(state)
    elif state.type == MoveNodeInlinedStateMachine.type:
        return _build_inlined_state_machine_nodes(state)
    else:
        raise TypeError("Invalid state node type '%s'" % state.type)


_xml_type_to_ui_type = {
    MoveNodeStateMachine.type: NodeStateMachine,
    MoveNodeTail.type: NodeTail,
    MoveNodeInlinedStateMachine.type: NodeInlinedStateMachine,
    MoveNodeBlend.type: NodeBlend,
    MoveNodeAddSubtract.type: NodeAddSubtract,
    MoveNodeFilter.type: NodeFilter,
    MoveNodeMirror.type: NodeMirror,
    MoveNodeFrame.type: NodeFrame,
    MoveNodeIk.type: NodeIk,
    MoveNodeBlendN.type: NodeBlendN,
    MoveNodeClip.type: NodeClip,
    MoveNodeExtrapolate.type: NodeExtrapolate,
    MoveNodeExpression.type: NodeExpression,
    MoveNodeCapture.type: NodeCapture,
    MoveNodeProxy.type: NodeProxy,
    MoveNodeAddN.type: NodeAddN,
    MoveNodeIdentity.type: NodeIdentity,
    MoveNodeMerge.type: NodeMerge,
    MoveNodePose.type: NodePose,
    MoveNodeMergeN.type: NodeMergeN,
    MoveNodeState.type: NodeState,
    MoveNodeInvalid.type: NodeInvalid,
    MoveNodeJointLimit.type: NodeJointLimit,
    MoveNodeSubNetwork.type: NodeSubNetwork
}


def create_anim_node_tree(tree: NodeTree, mn: MoveNodeBase, parent_frame=None):
    n = None
    if mn.type in _xml_type_to_ui_type:
        n = tree.nodes.new(_xml_type_to_ui_type[mn.type].bl_idname)
        n.init_from_xml(mn)
    else:
        raise TypeError("Invalid animation node type '%s'" % mn.type)

    # create children and connect them
    if isinstance(mn, MoveNodeWithChildBase):
        n_child = create_anim_node_tree(tree, mn.child, parent_frame)
        tree.links.new(n_child.outputs["output"], n.inputs["input"])
    elif isinstance(mn, MoveNodePairBase):
        n_child0 = create_anim_node_tree(tree, mn.child0, parent_frame)
        n_child1 = create_anim_node_tree(tree, mn.child1, parent_frame)
        tree.links.new(n_child0.outputs["output"], n.inputs["input0"])
        tree.links.new(n_child1.outputs["output"], n.inputs["input1"])
    elif isinstance(mn, MoveNodeNBase):
        for child in mn.children:
            n_child = create_anim_node_tree(tree, child.node, parent_frame)
            tree.links.new(n_child.outputs["output"], n.inputs["inputs"])

    if mn.type == MoveNodeStateMachine.type or mn.type == MoveNodeInlinedStateMachine.type:
        frame = build_state_nodes(tree, mn, parent_frame)
        if parent_frame is not None:
            frame.parent = parent_frame

    n.name = mn.name
    n.label = "%s (%s)" % (mn.name, n.bl_label)
    if parent_frame is not None:
        n.parent = parent_frame
    return n


def layout_node_tree(node_tree):
    frames = []
    for n in node_tree.nodes:
        if isinstance(n, bpy.types.NodeFrame):
            frames.append(n)
            continue

        if len(n.outputs) != 0:
            continue

        layout_node(n)

    parent_frames = {}
    for f in frames:
        if f.parent is None:
            continue
        if f.parent in parent_frames:
            parent_frames[f.parent].append(f)
        else:
            parent_frames[f.parent] = [f]

    gap_between_frames_x = 650
    gap_between_frames_y = 450
    frame_y = 0
    for parent, frames in parent_frames.items():
        frame_x = 0
        for f in frames:
            # only position innermost frames, Blender will resize/move the parent frames automatically
            # if f in parent_frames:
            #     continue
            f.location.x = frame_x
            f.location.y = frame_y
            # blender does not update node dimensions until the tree is drawn on screen :(
            # print(f.height, f.dimensions)
            frame_x += gap_between_frames_x
        frame_y -= gap_between_frames_y


def layout_node(node):
    # based on:
    # https://github.com/abego/treelayout/blob/master/org.abego.treelayout/src/main/java/org/abego/treelayout/TreeLayout.java#L593
    # BSD 3-Clause License
    #
    # Copyright (c) 2011, abego Software GmbH, Germany (http://www.abego.org)
    # All rights reserved.
    #
    _children_cache = {}

    prelim = {}
    mod = {}
    thread = {}
    ancestor = {}
    number = {}
    change = {}
    shift = {}
    size_of_level = []

    gap_between_levels = 100
    gap_between_nodes = 50
    node_size = 200

    def _get_child_nodes(node):
        if node in _children_cache:
            return _children_cache[node]

        child_nodes = []
        for input in node.inputs:
            for link in input.links:
                child = link.from_node
                if child in child_nodes:
                    continue
                else:
                    child_nodes.append(child)
        _children_cache[node] = child_nodes
        return child_nodes

    def _is_leaf(node):
        return len(node.inputs) == 0

    def _distance(v, w):
        size_of_nodes = node_size + node_size
        distance = size_of_nodes / 2 + gap_between_nodes
        return distance

    def _next_right(v):
        return thread.get(v, None) if _is_leaf(v) else _get_child_nodes(v)[-1]

    def _next_left(v):
        return thread.get(v, None) if _is_leaf(v) else _get_child_nodes(v)[0]

    def _ancestor(v_i_minus, v, v_parent, default_ancestor):
        anc = ancestor.get(v_i_minus, None)
        return anc if anc in _get_child_nodes(v_parent) else default_ancestor

    def _number(node, parent_node):
        n = number.get(node, None)
        if n is None:
            i = 1
            for child in _get_child_nodes(parent_node):
                number[child] = i
                i += 1
            n = number[node]

        return n

    def _move_subtree(w_minus, w_plus, parent, shift_val):
        subtrees = _number(w_plus, parent) - _number(w_minus, parent)
        change[w_plus] = change.get(w_plus, 0.0) - shift_val / subtrees
        shift[w_plus] = shift.get(w_plus, 0.0) + shift_val
        change[w_minus] = change.get(w_minus, 0.0) + shift_val / subtrees
        prelim[w_plus] = prelim.get(w_plus, 0.0) + shift_val
        mod[w_plus] = mod.get(w_plus, 0.0) + shift_val

    def _apportion(v, default_ancestor, left_sibling, v_parent):
        w = left_sibling
        if w is None:
            return default_ancestor

        v_o_plus = v
        v_i_plus = v
        v_i_minus = w
        v_o_minus = _get_child_nodes(v_parent)[0]

        s_i_plus = mod.get(v_i_plus, 0.0)
        s_o_plus = mod.get(v_o_plus, 0.0)
        s_i_minus = mod.get(v_i_minus, 0.0)
        s_o_minus = mod.get(v_o_minus, 0.0)

        next_right_v_i_minus = _next_right(v_i_minus)
        next_left_v_i_plus = _next_left(v_i_plus)

        while next_right_v_i_minus is not None and next_left_v_i_plus is not None:
            v_i_minus = next_right_v_i_minus
            v_i_plus = next_left_v_i_plus
            v_o_minus = _next_left(v_o_minus)
            v_o_plus = _next_right(v_o_plus)
            ancestor[v_o_plus] = v
            shift_val = (prelim.get(v_i_minus, 0.0) + s_i_minus) - (prelim.get(v_i_plus, 0.0) + s_i_plus) + _distance(v_i_minus, v_i_plus)
            if shift_val > 0.0:
                _move_subtree(_ancestor(v_i_minus, v, v_parent, default_ancestor), v, v_parent, shift_val)
                s_i_plus += shift_val
                s_o_plus += shift_val

            s_i_minus += mod.get(v_i_minus, 0.0)
            s_i_plus += mod.get(v_i_plus, 0.0)
            s_o_minus += mod.get(v_o_minus, 0.0)
            s_o_plus += mod.get(v_o_plus, 0.0)

            next_right_v_i_minus = _next_right(v_i_minus)
            next_left_v_i_plus = _next_left(v_i_plus)

        if next_right_v_i_minus is not None and _next_right(v_o_plus) is None:
            thread[v_o_plus] = next_right_v_i_minus
            mod[v_o_plus] = mod.get(v_o_plus, 0.0) + s_i_minus - s_o_plus

        if next_left_v_i_plus is not None and _next_left(v_o_minus) is None:
            thread[v_o_minus] = next_left_v_i_plus
            mod[v_o_minus] = mod.get(v_o_minus, 0.0) + s_i_plus - s_o_minus
            default_ancestor = v

        return default_ancestor

    def _execute_shifts(v):
        shift_val = 0.0
        change_val = 0.0
        for w in reversed(_get_child_nodes(v)):
            change_val += change.get(w, 0.0)
            prelim[w] = prelim.get(w, 0.0) + shift_val
            mod[w] = mod.get(w, 0.0) + shift_val
            shift_val += shift.get(w, 0.0) + change_val

    def _calc_size_of_levels(node, level):
        old_size = 0
        if len(size_of_level) <= level:
            size_of_level.append(0)
        else:
            old_size = size_of_level[level]

        size = node_size
        if old_size < size:
            size_of_level[level] = size

        if not _is_leaf(node):
            for child in _get_child_nodes(node):
                _calc_size_of_levels(child, level + 1)

    def _first_walk(node, left_sibling):
        v = node
        w = left_sibling
        if _is_leaf(v):
            if w is not None:
                prelim[v] = prelim.get(w, 0.0) + _distance(v, w)
        else:
            children = _get_child_nodes(v)
            default_ancestor = children[0]
            previous_child = None
            for c in children:
                _first_walk(c, previous_child)
                default_ancestor = _apportion(c, default_ancestor, previous_child, v)
                previous_child = c
            _execute_shifts(v)
            midpoint = (prelim.get(children[0], 0.0) + prelim.get(children[-1], 0.0)) / 2.0
            if w is not None:
                prelim[v] = prelim.get(w, 0.0) + _distance(v, w)
                mod[v] = prelim[v] - midpoint
            else:
                prelim[v] = midpoint

    def _second_walk(v, m, level, level_start):
        level_size = size_of_level[level]

        x = -(level_start + (level_size / 2))
        y = -(prelim.get(v, 0.0) + m)

        v.location.x = x
        v.location.y = y

        if not _is_leaf(v):
            next_level_start = level_start + (level_size + gap_between_levels)
            for c in _get_child_nodes(v):
                _second_walk(c, m + mod.get(v, 0.0), level + 1, next_level_start)

    _first_walk(node, None)
    _calc_size_of_levels(node, 0)
    _second_walk(node, -prelim.get(node, 0.0), 0, 0)
