import bpy
from .node_tree import NodeTree
from .node_socket import *
from ..properties import ParameterizedFloatProperty, ParameterizedBoolProperty
from ...cwxml.mrf import *


# BASE NODE CLASSES
class NodeBase(bpy.types.Node):
    bl_label = "Node"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == NodeTree.bl_idname

    def create_input(self, socket_type, socket_name, socket_label):
        if self.inputs.get(socket_name):
            return None

        input = self.inputs.new(socket_type, socket_name)
        input.text = socket_label
        return input

    def remove_input(self, socket_name):
        input = self.inputs.get(socket_name)
        if input:
            self.inputs.remove(input)

    def create_output(self, socket_type, socket_name, socket_label):
        if self.outputs.get(socket_name):
            return None

        output = self.outputs.new(socket_type, socket_name)
        output.text = socket_label
        return input

    def remove_output(self, socket_name):
        output = self.outputs.get(socket_name)
        if output:
            self.outputs.remove(output)

    def init_from_xml(self, node_xml):
        raise NotImplementedError


class NodeOutputAnimation(NodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeOutputAnimation'
    bl_label = 'Output Animation'

    def init(self, context):
        self.create_input(NodeSocket.bl_idname, "input", "Result")

    def init_from_xml(self, node_xml):
        raise Exception("NodeOutputAnimation cannot be initialized from XML")


# 0 inputs, 1 output
class Node0x1(NodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_Node0x1'

    def init(self, context):
        self.create_output(NodeSocket.bl_idname, "output", "Out")


# 1 input, 1 output
class Node1x1(NodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_Node1x1'

    def init(self, context):
        self.create_output(NodeSocket.bl_idname, "output", "Out")
        self.create_input(NodeSocket.bl_idname, "input", "In")


# 2 inputs, 1 output
class Node2x1(NodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_Node2x1'

    def init(self, context):
        self.create_output(NodeSocket.bl_idname, "output", "Out")
        self.create_input(NodeSocket.bl_idname, "input0", "A")
        self.create_input(NodeSocket.bl_idname, "input1", "B")


# N inputs, 1 output
class NodeNx1(NodeBase):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeNx1'

    def init(self, context):
        self.create_output(NodeSocket.bl_idname, "output", "Out")
        input = self.create_input(NodeSocket.bl_idname, "inputs", "In")
        # input.is_multi_input = True
        input.link_limit = 64  # .mrf uses 6 bits to store the children count


# IMPLEMENTED NODE CLASSES


class NodeStateMachine(Node0x1, bpy.types.NodeCustomGroup):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeStateMachine'
    bl_label = 'State Machine'

    def init_from_xml(self, node_xml: MoveNodeStateMachine):
        pass


class NodeTail(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeTail'
    bl_label = 'Tail'

    def init_from_xml(self, node_xml: MoveNodeTail):
        pass


class NodeInlinedStateMachine(Node0x1, bpy.types.NodeCustomGroup):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeInlinedStateMachine'
    bl_label = 'Inlined State Machine'

    def init_from_xml(self, node_xml: MoveNodeInlinedStateMachine):
        pass


class NodeBlend(Node2x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeBlend'
    bl_label = 'Blend'

    weight: bpy.props.PointerProperty(name='Weight', type=ParameterizedFloatProperty)

    def init_from_xml(self, node_xml: MoveNodeBlend):
        self.weight.set(node_xml.weight)

    def draw_buttons(self, context, layout):
        self.weight.draw("Weight", layout)


class NodeAddSubtract(Node2x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeAddSubtract'
    bl_label = 'Add-Subtract'

    def init_from_xml(self, node_xml: MoveNodeAddSubtract):
        pass


class NodeFilter(Node1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeFilter'
    bl_label = 'Filter'

    def init_from_xml(self, node_xml: MoveNodeFilter):
        pass


class NodeMirror(Node1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeMirror'
    bl_label = 'Mirror'

    def init_from_xml(self, node_xml: MoveNodeMirror):
        pass


class NodeFrame(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeFrame'
    bl_label = 'Frame'

    def init_from_xml(self, node_xml: MoveNodeFrame):
        pass


class NodeIk(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeIk'
    bl_label = 'IK'

    def init_from_xml(self, node_xml: MoveNodeIk):
        pass


class NodeBlendN(NodeNx1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeBlendN'
    bl_label = 'Blend N'

    def init_from_xml(self, node_xml: MoveNodeBlendN):
        pass


class NodeClip(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeClip'
    bl_label = 'Clip'

    phase: bpy.props.PointerProperty(name='Phase', type=ParameterizedFloatProperty)
    rate: bpy.props.PointerProperty(name='Rate', type=ParameterizedFloatProperty)
    delta: bpy.props.PointerProperty(name='Delta', type=ParameterizedFloatProperty)
    looped: bpy.props.PointerProperty(name='Looped', type=ParameterizedBoolProperty)

    def init_from_xml(self, node_xml: MoveNodeClip):
        self.phase.set(node_xml.phase)
        self.rate.set(node_xml.rate)
        self.delta.set(node_xml.delta)
        self.looped.set(node_xml.looped)

    def draw_buttons(self, context, layout):
        # self.clip
        self.phase.draw("Phase", layout)
        self.rate.draw("Rate", layout)
        self.delta.draw("Delta", layout)
        self.looped.draw("Looped", layout)
        # self.unk_flag10


class NodeExtrapolate(Node1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeExtrapolate'
    bl_label = 'Extrapolate'

    def init_from_xml(self, node_xml: MoveNodeExtrapolate):
        pass


class NodeExpression(Node1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeExpression'
    bl_label = 'Expression'

    def init_from_xml(self, node_xml: MoveNodeExpression):
        pass


class NodeCapture(Node1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeCapture'
    bl_label = 'Capture'

    def init_from_xml(self, node_xml: MoveNodeCapture):
        pass


class NodeProxy(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeProxy'
    bl_label = 'Proxy'

    def init_from_xml(self, node_xml: MoveNodeProxy):
        pass


class NodeAddN(NodeNx1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeAddN'
    bl_label = 'Add N'

    def init_from_xml(self, node_xml: MoveNodeAddN):
        pass


class NodeIdentity(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeIdentity'
    bl_label = 'Identity'

    def init_from_xml(self, node_xml: MoveNodeIdentity):
        pass


class NodeMerge(Node2x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeMerge'
    bl_label = 'Merge'

    def init_from_xml(self, node_xml: MoveNodeMerge):
        pass


class NodePose(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodePose'
    bl_label = 'Pose'

    def init_from_xml(self, node_xml: MoveNodePose):
        pass


class NodeMergeN(NodeNx1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeMergeN'
    bl_label = 'Merge N'

    def init_from_xml(self, node_xml: MoveNodeMergeN):
        pass


class NodeState(bpy.types.NodeCustomGroup):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeState'
    bl_label = 'State'

    def init(self, context):
        self.node_tree = bpy.data.node_groups.new(self.name, NodeTree.bl_idname)
        print(self.node_tree)
        if hasattr(self.node_tree, 'is_hidden'):
            self.node_tree.is_hidden = False
        self.node_tree.nodes.new('NodeGroupInput')
        self.node_tree.nodes.new('NodeGroupOutput')

    # Draw the node components
    # def draw_buttons(self, context, layout):
        #print("draw_buttons(...)")
        #row=layout.row()
        #row.prop(self, 'expressionText', text='Expression')
        #row=layout.row()
        #row.operator('node.node_dynamic_maths_expression_editwithin', text='Edit')

class NodeInvalid(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeInvalid'
    bl_label = 'Invalid'

    def init_from_xml(self, node_xml: MoveNodeInvalid):
        pass


class NodeJointLimit(Node1x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeJointLimit'
    bl_label = 'Joint Limit'

    def init_from_xml(self, node_xml: MoveNodeJointLimit):
        pass


class NodeSubNetwork(Node0x1):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeSubNetwork'
    bl_label = 'Sub-Network'

    def init_from_xml(self, node_xml: MoveNodeSubNetwork):
        pass


classes = [
    NodeOutputAnimation,
    NodeStateMachine,
    NodeTail,
    NodeInlinedStateMachine,
    NodeBlend,
    NodeAddSubtract,
    NodeFilter,
    NodeMirror,
    NodeFrame,
    NodeIk,
    NodeBlendN,
    NodeClip,
    NodeExtrapolate,
    NodeExpression,
    NodeCapture,
    NodeProxy,
    NodeAddN,
    NodeIdentity,
    NodeMerge,
    NodePose,
    NodeMergeN,
    NodeState,
    NodeInvalid,
    NodeJointLimit,
    NodeSubNetwork,
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
