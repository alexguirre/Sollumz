import bpy
from ..properties import ParameterizedFloatProperty, ParameterizedAssetProperty
from ...cwxml.mrf import MoveNodeNChildren


class ATNodeSocket(bpy.types.NodeSocket):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeSocket'
    bl_label = 'ATNodeSocket'

    text: bpy.props.StringProperty(name='Text', default='')
    socket_color = (0.85, 0.85, 0.85, 1)

    def draw(self, context, layout, node, text):
        layout.label(text=self.text)

    def draw_color(self, context, node):
        return self.socket_color


class ATNodeNSocket(bpy.types.NodeSocket):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_ATNodeNSocket'
    bl_label = 'ATNodeNSocket'

    text: bpy.props.StringProperty(name='Text', default='')
    socket_color = (0.85, 0.85, 0.85, 1)

    weight: bpy.props.PointerProperty(name="Weight", type=ParameterizedFloatProperty)
    frame_filter: bpy.props.PointerProperty(name="Frame Filter", type=ParameterizedAssetProperty)

    def draw(self, context, layout, node, text):
        self.weight.draw("Weight", context, layout)
        self.frame_filter.draw("Filter", context, layout)

    def draw_color(self, context, node):
        return self.socket_color

    def set(self, v: MoveNodeNChildren.Child):
        self.weight.set(v.weight)
        self.frame_filter.set(v.frame_filter)
