import bpy
from ..cwxml.mrf import *
from .ui.node_tree import NetworkTree
from .ui.nodes import *
import os


def import_mrf(filepath: str):
    mrf_xml = MRF.from_xml_file(filepath)
    MRF.write_xml(mrf_xml, "D:\\re\\gta5\\test.mrf.xml")
    move_network_to_obj(mrf_xml, os.path.basename(filepath.replace(MRF.file_extension, "")))


def move_network_to_obj(mrf_xml: MoveNetwork, name: str):
    # TODO: should we create a blender object for the MoVE network?
    build_move_network(mrf_xml, name)


def build_move_network(mrf_xml: MoveNetwork, name: str):
    # TODO: can we skip this root tree and just directly use the animation tree for root states
    # and state graph for root state machines?
    root_tree: NetworkTree = bpy.data.node_groups.new(name, NetworkTree.bl_idname)
    root_tree.network_tree_type = "STATE_MACHINE"
    root_node = root_tree.nodes.new(SMNodeStart.bl_idname)
    root_state_node = create_state_machine_graph_node(root_tree, mrf_xml.root_state)
    root_node.set_start_state(root_state_node)
    return root_tree


def create_state_machine_graph_tree(parent_name, state_machine):
    state_machine_graph_tree = bpy.data.node_groups.new(parent_name + "." + state_machine.name, NetworkTree.bl_idname)
    state_machine_graph_tree.network_tree_type = "STATE_MACHINE"

    states_nodes = {}
    states_by_name = {}
    for state in state_machine.states:
        states_nodes[state] = create_state_machine_graph_node(state_machine_graph_tree, state)
        states_nodes[state].name = state.name
        states_nodes[state].label = state.name
        states_by_name[state.name] = state

    for state, node in states_nodes.items():
        if state.transitions is None:
            continue
        for t in state.transitions:
            target_node = states_nodes[states_by_name[t.target_state]]
            node.add_transition(target_node)
    initial_node = states_nodes[states_by_name[state_machine.initial_state]]
    start_node = state_machine_graph_tree.nodes.new(SMNodeStart.bl_idname)
    start_node.name = "start"
    start_node.label = "Start"
    start_node.set_start_state(initial_node)

    layout_state_machine_graph_tree(state_machine_graph_tree)

    return state_machine_graph_tree


def create_state_machine_graph_node(sm_tree: NetworkTree, mn: MoveNodeBase):
    if sm_tree.network_tree_type != "STATE_MACHINE":
        raise Exception("Expected a state machine graph tree, found '%s'" % sm_tree.network_tree_type)

    state_node = None
    if mn.type == MoveNodeState.type:
        state_node = sm_tree.nodes.new(SMNodeState.bl_idname)
        state_node.name = mn.name
        state_node.label = "%s (State)" % mn.name

        state_node.animation_tree = create_animation_tree(sm_tree.name, mn.name, mn.initial_node)

    elif mn.type == MoveNodeStateMachine.type:
        state_node = sm_tree.nodes.new(SMNodeState.bl_idname)
        state_node.name = mn.name
        state_node.label = "%s (State Machine)" % mn.name

        state_node.state_machine_tree = create_state_machine_graph_tree(sm_tree.name, mn)

    elif mn.type == MoveNodeInlinedStateMachine.type:
        state_node = sm_tree.nodes.new(SMNodeState.bl_idname)
        state_node.name = mn.name
        state_node.label = "%s (Inlined State Machine)" % mn.name

        state_node.state_machine_tree = create_state_machine_graph_tree(sm_tree.name, mn)
        state_node.animation_tree = create_animation_tree(sm_tree.name, mn.name + ".fallback", mn.fallback_node)

    else:
        raise TypeError("Invalid state node type '%s'" % mn.type)

    return state_node


_nodes_xml_type_to_animation_tree_type = {
    MoveNodeStateMachine.type: ATNodeStateMachine,
    MoveNodeTail.type: ATNodeTail,
    MoveNodeInlinedStateMachine.type: ATNodeInlinedStateMachine,
    MoveNodeBlend.type: ATNodeBlend,
    MoveNodeAddSubtract.type: ATNodeAddSubtract,
    MoveNodeFilter.type: ATNodeFilter,
    MoveNodeMirror.type: ATNodeMirror,
    MoveNodeFrame.type: ATNodeFrame,
    MoveNodeIk.type: ATNodeIk,
    MoveNodeBlendN.type: ATNodeBlendN,
    MoveNodeClip.type: ATNodeClip,
    MoveNodeExtrapolate.type: ATNodeExtrapolate,
    MoveNodeExpression.type: ATNodeExpression,
    MoveNodeCapture.type: ATNodeCapture,
    MoveNodeProxy.type: ATNodeProxy,
    MoveNodeAddN.type: ATNodeAddN,
    MoveNodeIdentity.type: ATNodeIdentity,
    MoveNodeMerge.type: ATNodeMerge,
    MoveNodePose.type: ATNodePose,
    MoveNodeMergeN.type: ATNodeMergeN,
    MoveNodeState.type: ATNodeState,
    MoveNodeInvalid.type: ATNodeInvalid,
    MoveNodeJointLimit.type: ATNodeJointLimit,
    MoveNodeSubNetwork.type: ATNodeSubNetwork
}


def create_animation_tree(parent_name, name, mn: MoveNodeBase):
    animation_tree = bpy.data.node_groups.new(parent_name + "." + name, NetworkTree.bl_idname)
    animation_tree.network_tree_type = "ANIMATION_TREE"
    final_output = animation_tree.nodes.new(ATNodeOutputAnimation.bl_idname)
    root_node = create_animation_tree_nodes(animation_tree, mn)
    animation_tree.links.new(root_node.outputs["output"], final_output.inputs["input"])
    layout_animation_tree(animation_tree)
    return animation_tree


def create_animation_tree_nodes(animation_tree: NetworkTree, mn: MoveNodeBase):
    if animation_tree.network_tree_type != "ANIMATION_TREE":
        raise Exception("Expected an animation tree tree, found '%s'" % animation_tree.network_tree_type)

    n = None
    if mn.type in _nodes_xml_type_to_animation_tree_type:
        n = animation_tree.nodes.new(_nodes_xml_type_to_animation_tree_type[mn.type].bl_idname)
        n.init_from_xml(mn)
    else:
        raise TypeError("Invalid animation node type '%s'" % mn.type)

    # create children and connect them
    if isinstance(mn, MoveNodeWithChildBase):
        n_child = create_animation_tree_nodes(animation_tree, mn.child)
        animation_tree.links.new(n_child.outputs["output"], n.inputs["input"])
    elif isinstance(mn, MoveNodePairBase):
        n_child0 = create_animation_tree_nodes(animation_tree, mn.child0)
        n_child1 = create_animation_tree_nodes(animation_tree, mn.child1)
        animation_tree.links.new(n_child0.outputs["output"], n.inputs["input0"])
        animation_tree.links.new(n_child1.outputs["output"], n.inputs["input1"])
    elif isinstance(mn, MoveNodeNBase):
        for child in mn.children:
            n_child = create_animation_tree_nodes(animation_tree, child.node)
            animation_tree.links.new(n_child.outputs["output"], n.inputs["inputs"])

    if mn.type == MoveNodeStateMachine.type:
        n.state_machine_tree = create_state_machine_graph_tree(animation_tree.name, mn)
    elif mn.type == MoveNodeInlinedStateMachine.type:
        n.state_machine_tree = create_state_machine_graph_tree(animation_tree.name, mn)
        n.fallback_animation_tree = create_animation_tree(animation_tree.name, mn.name + ".fallback", mn.fallback_node)
    elif mn.type == MoveNodeState.type:
        raise "Can states appear directly in animation trees?"

    n.name = mn.name
    n.label = "%s (%s)" % (mn.name, n.bl_label)
    return n


def layout_state_machine_graph_tree(node_tree):
    pass


def layout_animation_tree(node_tree):
    for n in node_tree.nodes:
        if len(n.outputs) != 0:
            continue

        layout_animation_tree_node(n)


def layout_animation_tree_node(node):
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
