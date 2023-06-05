import bpy
from ..nodes.node_tree import NetworkTree

class NetworkPropertiesPanel(bpy.types.Panel):
    bl_label = "Properties"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_NetworkPropertiesPanel"
    bl_category = "Network"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == NetworkTree.bl_idname and
                context.space_data.edit_tree is not None and
                context.space_data.edit_tree.bl_idname == NetworkTree.bl_idname)

    def draw(self, context):
        node_tree = context.space_data.edit_tree
        if node_tree.network_root is not None:
            node_tree = node_tree.network_root

        self.layout.prop(node_tree, 'name')
        for prop in node_tree.__annotations__:
            self.layout.prop(node_tree, prop)


class AnimationTreePropertiesPanel(bpy.types.Panel):
    bl_label = "Properties"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_AnimationTreePropertiesPanel"
    bl_category = "Animation Tree"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == 'ANIMATION_TREE')

    def draw(self, context):
        node_tree = context.space_data.edit_tree

        self.layout.prop(node_tree, 'name')
        for prop in node_tree.__annotations__:
            self.layout.prop(node_tree, prop)


class StateMachineActiveTransitionPanel(bpy.types.Panel):
    """
    Panel for editing the active transition properties.
    The active transition is the one clicked by the user (see editor_state_machine_input operator).
    """
    bl_label = "Transition"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_StateMachineActiveTransitionPanel"
    bl_category = "State Machine"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == 'STATE_MACHINE' and
                space.edit_tree.ui_active_transition_source_node_name != "")

    def draw(self, context):
        node_tree = context.space_data.edit_tree
        source_node = node_tree.nodes[node_tree.ui_active_transition_source_node_name]
        transition = source_node.transitions[node_tree.ui_active_transition_index]

        for prop in transition.__annotations__:
            self.layout.prop(transition, prop)


class StateMachinePropertiesPanel(bpy.types.Panel):
    bl_label = "Properties"
    bl_idname = "SOLLUMZ_PT_MOVE_NETWORK_StateMachinePropertiesPanel"
    bl_category = "State Machine"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname and
                space.edit_tree.network_tree_type == 'STATE_MACHINE')

    def draw(self, context):
        node_tree = context.space_data.edit_tree

        self.layout.prop(node_tree, 'name')
        for prop in node_tree.__annotations__:
            self.layout.prop(node_tree, prop)
