import bpy


# NodeTree code based on: https://github.com/atticus-lv/simple_node_tree
class NodeTree(bpy.types.NodeTree):
    bl_idname = "SOLLUMZ_NT_MOVE_NETWORK_NodeTree"
    bl_label = "MoVE Network Editor"
    bl_icon = "ONIONSKIN_ON"

    test1: bpy.props.StringProperty(name="Test1")
    test2: bpy.props.StringProperty(name="Test2")
    test3: bpy.props.IntProperty(name="Test3")


class NodeTreePropertiesPanel(bpy.types.Panel):
    bl_label = "Properties"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_NodeTreePropertiesPanel"
    bl_category = "Network"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == NodeTree.bl_idname and
                context.space_data.edit_tree is not None and
                context.space_data.edit_tree.bl_idname == NodeTree.bl_idname)

    def draw(self, context):
        node_tree = context.space_data.edit_tree
        self.layout.prop(node_tree, 'name')
        for prop in node_tree.__annotations__:
            self.layout.prop(node_tree, prop)
