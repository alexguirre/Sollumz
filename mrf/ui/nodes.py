import bpy
from .node_tree import NodeTree
from .node_socket import *


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


class NodeOutputAnimation(NodeBase):
    bl_idname = 'SOLLUMZ_NT_OutputAnimation'
    bl_label = 'Output Animation'

    def init(self, context):
        self.create_input(NodeSocket.bl_idname, "input", "Result")


class NodeWithOutput(NodeBase):
    bl_idname = 'SOLLUMZ_NT_NodeWithOutput'

    def init(self, context):
        self.create_output(NodeSocket.bl_idname, "output", "Out")


class NodeEmpty(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Empty'
    bl_label = 'Empty'


class NodeClip(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Clip'
    bl_label = 'Clip'

    clip_container: bpy.props.StringProperty(name='Clip Container', default='')
    clip: bpy.props.StringProperty(name='Clip', default='')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'clip_container')
        layout.prop(self, 'clip')


class NodeBlend(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Blend'
    bl_label = 'Blend'

    def init(self, context):
        super().init(context)
        self.create_input(NodeSocket.bl_idname, "input1", "A")
        self.create_input(NodeSocket.bl_idname, "input2", "B")


class NodeFilter(NodeWithOutput):
    bl_idname = 'SOLLUMZ_NT_Filter'
    bl_label = 'Filter'

    def init(self, context):
        super().init(context)
        self.create_input(NodeSocket.bl_idname, "input", "In")


# class NodeState(NodeBase):
#     bl_idname = 'SOLLUMZ_NT_NodeState'
#     bl_label = 'State'
#
#     def init(self, context):
#         self.create_input(NodeSocketInt.bl_idname, 'value', 'Value')
#
#
# class NodeStateMachine(NodeBase):
#     bl_idname = 'SOLLUMZ_NT_NodeStateMachine'
#     bl_label = 'State Machine'
#
#     def init(self, context):
#         self.create_input(NodeSocketFloat.bl_idname, 'value1', 'Value')
#         self.create_input(NodeSocketFloat.bl_idname, 'value2', 'Value')
#         self.create_output(NodeSocketFloat.bl_idname, 'output', "Output")

# import traceback
# import sys
called = False
def register():
    global called
    if called: # TODO: investigate why register() is getting called twice
        return
    called = True
    # print("nodes register <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    # traceback.print_stack(file=sys.stdout)
    bpy.utils.register_class(NodeOutputAnimation)
    bpy.utils.register_class(NodeEmpty)
    bpy.utils.register_class(NodeClip)
    bpy.utils.register_class(NodeBlend)
    bpy.utils.register_class(NodeFilter)


def unregister():
    bpy.utils.unregister_class(NodeOutputAnimation)
    bpy.utils.unregister_class(NodeEmpty)
    bpy.utils.unregister_class(NodeClip)
    bpy.utils.unregister_class(NodeBlend)
    bpy.utils.unregister_class(NodeFilter)
