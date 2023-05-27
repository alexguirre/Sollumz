import bpy


class NodeSocket(bpy.types.NodeSocket):
    bl_idname = 'SOLLUMZ_NT_NodeSocket'
    bl_label = 'NodeSocket'

    text: bpy.props.StringProperty(name='Text', default='')
    socket_color = (0.85, 0.85, 0.85, 1)

    def draw(self, context, layout, node, text):
        layout.label(text=self.text)

    def draw_color(self, context, node):
        return self.socket_color


def register():
    pass # bpy.utils.register_class(NodeSocket)


def unregister():
    pass # bpy.utils.unregister_class(NodeSocket)
