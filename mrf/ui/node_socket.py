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


class NodeSocketTransitionSource(bpy.types.NodeSocket):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeSocketTransitionSource'
    bl_label = 'NodeSocketTransitionSource'

    duration: bpy.props.FloatProperty(name='Duration', default=0.0)
    value: bpy.props.IntProperty(name='Value', default=0)

    socket_color = (0.15, 0.75, 0.15, 1)

    def draw(self, context, layout, node, text):
        layout.prop(self, 'duration')
        layout.prop(self, 'value')

    def draw_color(self, context, node):
        return self.socket_color


class NodeSocketTransitionTarget(bpy.types.NodeSocket):
    bl_idname = 'SOLLUMZ_NT_MOVE_NETWORK_NodeSocketTransitionTarget'
    bl_label = 'NodeSocketTransitionTarget'

    socket_color = (0.15, 0.35, 0.15, 1)

    def draw(self, context, layout, node, text):
        pass

    def draw_color(self, context, node):
        return self.socket_color


def register():
    pass # bpy.utils.register_class(NodeSocket)


def unregister():
    pass # bpy.utils.unregister_class(NodeSocket)
