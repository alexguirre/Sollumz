import bpy
from abc import ABC as AbstractClass, abstractmethod
from .node_tree import NodeTree
from .node_socket import *
from ..properties import ParameterizedFloatProperty, ParameterizedBoolProperty
from ...cwxml.mrf import *


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

    def remove_input(self, socket_name):
        input = self.inputs.get(socket_name)
        if input:
            self.inputs.remove(input)

    def create_output(self, socket_type, socket_name, socket_label):
        if self.outputs.get(socket_name):
            return None

        output = self.outputs.new(socket_type, socket_name)
        output.text = socket_label

    def remove_output(self, socket_name):
        output = self.outputs.get(socket_name)
        if output:
            self.outputs.remove(output)

    @abstractmethod
    def init_from_xml(self, node_xml):
        raise NotImplementedError


class NodeOutputAnimation(NodeBase):
    bl_idname = 'SOLLUMZ_NT_OutputAnimation'
    bl_label = 'Output Animation'

    def init(self, context):
        self.create_input(NodeSocket.bl_idname, "input", "Result")

    def init_from_xml(self, node_xml):
        raise Exception("NodeOutputAnimation cannot be initialized from XML")


class NodeWithOutput(NodeBase):
    bl_idname = 'SOLLUMZ_NT_NodeWithOutput'

    def init(self, context):
        self.create_output(NodeSocket.bl_idname, "output", "Out")


class NodeEmpty(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Empty'
    bl_label = 'Empty'

    def init_from_xml(self, node_xml: MoveNodeInvalid):
        pass


class NodeClip(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Clip'
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


class NodeBlend(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Blend'
    bl_label = 'Blend'

    weight: bpy.props.PointerProperty(name='Weight', type=ParameterizedFloatProperty)

    def init_from_xml(self, node_xml: MoveNodeBlend):
        self.weight.set(node_xml.weight)

    def init(self, context):
        super().init(context)
        self.create_input(NodeSocket.bl_idname, "input1", "A")
        self.create_input(NodeSocket.bl_idname, "input2", "B")

    def draw_buttons(self, context, layout):
        self.weight.draw("Weight", layout)


class NodeBlendN(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_BlendN'
    bl_label = 'Blend N'

    def init_from_xml(self, node_xml: MoveNodeBlendN):
        pass

    def init(self, context):
        super().init(context)


class NodeAddSubtract(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_AddSubtract'
    bl_label = 'Add-Subtract'

    def init_from_xml(self, node_xml: MoveNodeAddSubtract):
        pass

    def init(self, context):
        super().init(context)
        self.create_input(NodeSocket.bl_idname, "input1", "A")
        self.create_input(NodeSocket.bl_idname, "input2", "B")


class NodeFilter(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Filter'
    bl_label = 'Filter'

    def init_from_xml(self, node_xml: MoveNodeFilter):
        pass

    def init(self, context):
        super().init(context)
        self.create_input(NodeSocket.bl_idname, "input", "In")


class NodeExpression(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Expression'
    bl_label = 'Expression'

    def init_from_xml(self, node_xml: MoveNodeExpression):
        pass

    def init(self, context):
        super().init(context)
        self.create_input(NodeSocket.bl_idname, "input", "In")


class NodeState(bpy.types.NodeCustomGroup):
    bl_idname = 'SOLLUMZ_NT_NodeState'
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



class NodeStateMachine(NodeWithOutput, bpy.types.NodeCustomGroup):
    bl_idname = 'SOLLUMZ_NT_StateMachine'
    bl_label = 'State Machine'

    def init_from_xml(self, node_xml: MoveNodeStateMachine):
        pass


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
    bpy.utils.register_class(NodeOutputAnimation)
    bpy.utils.register_class(NodeEmpty)
    bpy.utils.register_class(NodeClip)
    bpy.utils.register_class(NodeBlend)
    bpy.utils.register_class(NodeBlendN)
    bpy.utils.register_class(NodeAddSubtract)
    bpy.utils.register_class(NodeFilter)
    bpy.utils.register_class(NodeExpression)
    bpy.utils.register_class(NodeState)
    bpy.utils.register_class(NodeStateMachine)


def unregister():
    bpy.utils.unregister_class(NodeOutputAnimation)
    bpy.utils.unregister_class(NodeEmpty)
    bpy.utils.unregister_class(NodeClip)
    bpy.utils.unregister_class(NodeBlend)
    bpy.utils.unregister_class(NodeBlendN)
    bpy.utils.unregister_class(NodeAddSubtract)
    bpy.utils.unregister_class(NodeFilter)
    bpy.utils.unregister_class(NodeExpression)
    bpy.utils.unregister_class(NodeState)
    bpy.utils.unregister_class(NodeStateMachine)
