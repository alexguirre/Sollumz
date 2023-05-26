import os

import bpy
from ..cwxml.mrf import MRF, MoveNetwork, MoveStateMachine, MoveState, MoveNode
from ..tools.blenderhelper import create_empty_object
from ..sollumz_properties import SollumType
from .properties import MoveNetworkProperties, MoveNetworkBitProperties
from .ui.node_tree import NodeTree
from .ui.nodes import *


def import_mrf(filepath: str):
    mrf_xml = MRF.from_xml_file(filepath)
    MRF.write_xml(mrf_xml, "D:\\re\\gta5\\test.mrf.xml")
    move_network_to_obj(mrf_xml, os.path.basename(filepath.replace(MRF.file_extension, "")))


def move_network_to_obj(mrf_xml: MoveNetwork, name: str):
    move_network_obj = create_empty_object(SollumType.MOVE_NETWORK, name)

    set_move_network_properties(mrf_xml, move_network_obj)

    build_node_tree(mrf_xml, name)


def set_move_network_properties(mrf_xml: MoveNetwork, obj: bpy.types.Object):
    obj.move_network_properties.test = 1234

    for trigger in mrf_xml.triggers:
        trigger_props = obj.move_network_properties.triggers.add()
        trigger_props.name = trigger.name
        trigger_props.bit_position = trigger.bit_position
    for flag in mrf_xml.flags:
        flag_props = obj.move_network_properties.flags.add()
        flag_props.name = flag.name
        flag_props.bit_position = flag.bit_position


def build_node_tree(mrf_xml: MoveNetwork, name: str):
    tree: NodeTree = bpy.data.node_groups.new(name, NodeTree.bl_idname)
    build_state_nodes(tree, mrf_xml.root_state)
    return tree


def build_state_nodes(tree: NodeTree, state):
    def _build_state_nodes(s: MoveState):
        # n = tree.nodes.new(NodeState.bl_idname)
        # n.name = s.name
        final_output = tree.nodes.new(NodeOutputAnimation.bl_idname)
        root_node = create_anim_node_tree(tree, s.initial_node)
        tree.links.new(root_node.outputs["output"], final_output.inputs["input"])
        # return n

    def _build_state_machine_nodes(sm: MoveStateMachine):
        # n = tree.nodes.new(NodeStateMachine.bl_idname)
        # n.name = sm.name
        for child in sm.states:
            build_state_nodes(tree, child)
            # tree.links.new(node1.inputs["Geometry"], node2.outputs["Geometry"])
        # return n

    if state.type == "State":
        return _build_state_nodes(state)
    elif state.type == "StateMachine":
        return _build_state_machine_nodes(state)
    else:
        raise TypeError("Invalid state node type '%s'" % state.type)


def create_anim_node_tree(tree: NodeTree, mn: MoveNode):
    n = None
    if mn.type == "Invalid":
        n = tree.nodes.new(NodeEmpty.bl_idname)
    elif mn.type == "Clip":
        n = tree.nodes.new(NodeClip.bl_idname)
        # n.clip_container = mn.clip.container_name
        # n.clip = mn.clip.name
    elif mn.type == "Blend":
        n = tree.nodes.new(NodeBlend.bl_idname)
        n_child0 = create_anim_node_tree(tree, mn.child0)
        n_child1 = create_anim_node_tree(tree, mn.child1)
        tree.links.new(n_child0.outputs["output"], n.inputs["input1"])
        tree.links.new(n_child1.outputs["output"], n.inputs["input2"])
    elif mn.type == "Filter":
        n = tree.nodes.new(NodeFilter.bl_idname)
        n_child = create_anim_node_tree(tree, mn.child)
        tree.links.new(n_child.outputs["output"], n.inputs["input"])
    else:
        raise TypeError("Invalid animation node type '%s'" % mn.type)

    n.name = mn.name
    n.label = "%s (%s)" % (mn.name, mn.type)
    return n
