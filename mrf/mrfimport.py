import bpy
from ..cwxml.mrf import *
from .nodes.node_tree import NetworkTree
from .nodes.nodes import *
from .nodes.layout import layout_animation_tree, layout_state_machine_graph_tree
import os


def import_mrf(filepath: str):
    mrf_xml = MRF.from_xml_file(filepath)
    build_move_network(mrf_xml, os.path.basename(filepath.replace(MRF.file_extension, "")))


def build_move_network(mrf_xml: MoveNetwork, name: str):
    # TODO: can we skip this root tree and just directly use the animation tree for root states
    # and state graph for root state machines?
    root_tree: NetworkTree = bpy.data.node_groups.new(name, NetworkTree.bl_idname)
    root_tree.network_tree_type = "ROOT"
    root_tree.network_root = None
    root_node = root_tree.nodes.new(SMNodeStart.bl_idname)
    root_state_node = create_state_machine_graph_node(root_tree, mrf_xml.root_state, root_tree)
    root_node.set_start_state(root_state_node)
    return root_tree


def create_state_machine_graph_tree(parent_name, state_machine, network_root: NetworkTree):
    state_machine_graph_tree = bpy.data.node_groups.new(parent_name + "." + state_machine.name, NetworkTree.bl_idname)
    state_machine_graph_tree.network_tree_type = "STATE_MACHINE"
    state_machine_graph_tree.network_root = network_root

    states_nodes = {}
    states_by_name = {}
    for state in state_machine.states:
        states_nodes[state] = create_state_machine_graph_node(state_machine_graph_tree, state, network_root)
        states_nodes[state].name = state.name
        states_nodes[state].label = state.name
        states_by_name[state.name] = state

    for state, node in states_nodes.items():
        if state.transitions is None:
            continue
        for t in state.transitions:
            target_node = states_nodes[states_by_name[t.target_state]]
            node.add_transition(target_node, t)
    initial_node = states_nodes[states_by_name[state_machine.initial_state]]
    start_node = state_machine_graph_tree.nodes.new(SMNodeStart.bl_idname)
    start_node.name = "start"
    start_node.label = "Start"
    start_node.set_start_state(initial_node)

    layout_state_machine_graph_tree(state_machine_graph_tree)

    return state_machine_graph_tree


def create_state_machine_graph_node(sm_tree: NetworkTree, mn: MoveNodeBase, network_root: NetworkTree):
    if sm_tree.network_tree_type not in {"STATE_MACHINE", "ROOT"}:
        raise Exception("Expected a state machine graph tree, found '%s'" % sm_tree.network_tree_type)

    state_node = None
    if mn.type == MoveNodeState.type:
        state_node = sm_tree.nodes.new(SMNodeState.bl_idname)
        state_node.name = mn.name
        state_node.label = "%s (State)" % mn.name

        state_node.animation_tree = create_animation_tree(sm_tree.name, mn.name, mn.initial_node, network_root, mn)

    elif mn.type == MoveNodeStateMachine.type:
        state_node = sm_tree.nodes.new(SMNodeStateMachine.bl_idname)
        state_node.name = mn.name
        state_node.label = "%s (State Machine)" % mn.name

        state_node.state_machine_tree = create_state_machine_graph_tree(sm_tree.name, mn, network_root)
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
    MoveNodeInvalid.type: ATNodeInvalid,
    MoveNodeJointLimit.type: ATNodeJointLimit,
    MoveNodeSubNetwork.type: ATNodeSubNetwork
}


def create_animation_tree(parent_name, name, mn: MoveNodeBase, network_root: NetworkTree, parent_state: MoveNodeState):
    animation_tree = bpy.data.node_groups.new(parent_name + "." + name, NetworkTree.bl_idname)
    animation_tree.network_tree_type = "ANIMATION_TREE"
    animation_tree.network_root = network_root
    final_output = animation_tree.nodes.new(ATNodeOutputAnimation.bl_idname)
    root_node = create_animation_tree_nodes(animation_tree, mn, network_root, parent_state)
    animation_tree.links.new(root_node.outputs["output"], final_output.inputs["input"])
    layout_animation_tree(animation_tree)
    return animation_tree


def create_animation_tree_nodes(animation_tree: NetworkTree, mn: MoveNodeBase, network_root: NetworkTree, parent_state: MoveNodeState):
    if animation_tree.network_tree_type != "ANIMATION_TREE":
        raise Exception("Expected an animation tree tree, found '%s'" % animation_tree.network_tree_type)

    n = None
    if mn.type in _nodes_xml_type_to_animation_tree_type:
        n = animation_tree.nodes.new(_nodes_xml_type_to_animation_tree_type[mn.type].bl_idname)
        assign_state_data_to_animation_tree_node(parent_state, n, mn)
        n.init_from_xml(mn)
        n.add_required_parameters_to_network(network_root)
    else:
        raise TypeError("Invalid animation node type '%s'" % mn.type)

    # create children and connect them
    if isinstance(mn, MoveNodeWithChildBase):
        n_child = create_animation_tree_nodes(animation_tree, mn.child, network_root, parent_state)
        animation_tree.links.new(n_child.outputs["output"], n.inputs["input"])
    elif isinstance(mn, MoveNodePairBase):
        n_child0 = create_animation_tree_nodes(animation_tree, mn.child0, network_root, parent_state)
        n_child1 = create_animation_tree_nodes(animation_tree, mn.child1, network_root, parent_state)
        animation_tree.links.new(n_child0.outputs["output"], n.inputs["input0"])
        animation_tree.links.new(n_child1.outputs["output"], n.inputs["input1"])
    elif isinstance(mn, MoveNodeNBase):
        for i, child in enumerate(mn.children):
            n_child = create_animation_tree_nodes(animation_tree, child.node, network_root, parent_state)
            animation_tree.links.new(n_child.outputs["output"], n.inputs[f"input{i}"])

    if mn.type == MoveNodeStateMachine.type:
        n.state_machine_tree = create_state_machine_graph_tree(animation_tree.name, mn, network_root)
    elif mn.type == MoveNodeInlinedStateMachine.type:
        n.state_machine_tree = create_state_machine_graph_tree(animation_tree.name, mn, network_root)
        n.fallback_animation_tree = create_animation_tree(animation_tree.name, mn.name + ".fallback",
                                                          mn.fallback_node, network_root, parent_state)

    n.name = mn.name
    n.label = "%s (%s)" % (mn.name, n.bl_label)
    return n


def assign_state_data_to_animation_tree_node(parent_state: MoveNodeState, node: AnimationTreeNodeBase, node_xml: MoveNodeBase):
    """Assigns the state input_parameters, output_parameters, events and operations corresponding to the given node."""
    node_index = node_xml.node_index
    for op in parent_state.input_parameters:
        if op.target_node_index == node_index:
            node_ip = node.input_parameters.add()
            node_ip.source_parameter_name = op.source_parameter_name
            node_ip.target_node_type = node_xml.type
            node_ip.set_target_node_parameter_id(op.target_node_parameter_id)
            node_ip.target_node_parameter_extra_arg = op.target_node_parameter_extra_arg
    for op in parent_state.output_parameters:
        if op.source_node_index == node_index:
            node_op = node.output_parameters.add()
            node_op.target_parameter_name = op.target_parameter_name
            node_op.source_node_type = node_xml.type
            node_op.set_source_node_parameter_id(op.source_node_parameter_id)
            node_op.source_node_parameter_extra_arg = op.source_node_parameter_extra_arg
    for evt in parent_state.events:
        if evt.node_index == node_index:
            node_evt = node.events.add()
            node_evt.node_type = node_xml.type
            node_evt.set_node_event_id(evt.node_event_id)
            node_evt.parameter_name = evt.parameter_name
    for ops in parent_state.operations:
        if ops.node_index == node_index:
            node_ops = node.operations.add()
            node_ops.node_type = node_xml.type
            node_ops.set_node_parameter_id(ops.node_parameter_id)
            node_ops.node_parameter_extra_arg = ops.node_parameter_extra_arg
            for operator in ops.operators:
                if operator.type == "Finish":
                    # the finish marker is not necessary in the node operators
                    # TODO: make Finish implicit and remove it from XML on CW
                    break
                node_ops.operators.add().set(operator)
