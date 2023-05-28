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
        if state_machine_frame is not None:
            state_machine_frame.parent = parent_frame
        for child in sm.states:
            build_state_nodes(tree, child, parent_frame=state_machine_frame)
        return state_machine_frame

    if state.type == MoveNodeState.type:
        return _build_state_nodes(state)
    elif state.type == MoveNodeStateMachine.type:
        return _build_state_machine_nodes(state)
    else:
        raise TypeError("Invalid state node type '%s'" % state.type)

def create_anim_node_tree(tree: NodeTree, mn: MoveNodeBase, parent_frame=None):
    n = None
    if mn.type == MoveNodeStateMachine.type:
        n = tree.nodes.new(NodeStateMachine.bl_idname)
        n.init_from_xml(mn)
        frame = build_state_nodes(tree, mn, parent_frame)
        if parent_frame is not None:
            frame.parent = parent_frame
    if mn.type == MoveNodeInvalid.type:
        n = tree.nodes.new(NodeEmpty.bl_idname)
        n.init_from_xml(mn)
    elif mn.type == MoveNodeClip.type:
        n = tree.nodes.new(NodeClip.bl_idname)
        n.init_from_xml(mn)
    elif mn.type == MoveNodeBlend.type:
        n = tree.nodes.new(NodeBlend.bl_idname)
        n.init_from_xml(mn)
        n_child0 = create_anim_node_tree(tree, mn.child0, parent_frame)
        n_child1 = create_anim_node_tree(tree, mn.child1, parent_frame)
        tree.links.new(n_child0.outputs["output"], n.inputs["input1"])
        tree.links.new(n_child1.outputs["output"], n.inputs["input2"])
    elif mn.type == MoveNodeAddSubtract.type:
        n = tree.nodes.new(NodeAddSubtract.bl_idname)
        n.init_from_xml(mn)
        n_child0 = create_anim_node_tree(tree, mn.child0, parent_frame)
        n_child1 = create_anim_node_tree(tree, mn.child1, parent_frame)
        tree.links.new(n_child0.outputs["output"], n.inputs["input1"])
        tree.links.new(n_child1.outputs["output"], n.inputs["input2"])
    elif mn.type == MoveNodeFilter.type:
        n = tree.nodes.new(NodeFilter.bl_idname)
        n.init_from_xml(mn)
        n_child = create_anim_node_tree(tree, mn.child, parent_frame)
        tree.links.new(n_child.outputs["output"], n.inputs["input"])
    elif mn.type == MoveNodeExpression.type:
        n = tree.nodes.new(NodeExpression.bl_idname)
        n.init_from_xml(mn)
        n_child = create_anim_node_tree(tree, mn.child, parent_frame)
        tree.links.new(n_child.outputs["output"], n.inputs["input"])
    elif mn.type == MoveNodeBlendN.type:
        n = tree.nodes.new(NodeBlendN.bl_idname)
        n.init_from_xml(mn)
        i = 1
        for child in mn.children:
            input_socket = "input%d" % i
            n.create_input(NodeSocket.bl_idname, input_socket, "#%d" % i)
            n_child = create_anim_node_tree(tree, child.node, parent_frame)
            tree.links.new(n_child.outputs["output"], n.inputs[input_socket])
            i += 1
    elif mn.type == MoveNodeStateMachine.type:
        n = tree.nodes.new(NodeStateMachine.bl_idname)
        n.init_from_xml(mn)
        frame = build_state_nodes(tree, mn, parent_frame)
        if parent_frame is not None:
            frame.parent = parent_frame
    else:
        raise TypeError("Invalid animation node type '%s'" % mn.type)

    n.name = mn.name
    n.label = "%s (%s)" % (mn.name, n.bl_label)
    if parent_frame is not None:
        n.parent = parent_frame
    return n
