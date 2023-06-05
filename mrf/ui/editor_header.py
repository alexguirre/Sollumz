import bpy
import bl_ui
from ..nodes.node_tree import NetworkTree


class NODE_HT_header(bl_ui.space_node.NODE_HT_header):
    """
    Overwrite the header of the node editor.
    Mainly to limit the tree selection to root MoVE network trees.
    """
    # TODO: can we overwrite this only for the MoVE network editor? The current approach may make sollumz
    #  imcompatible with other addons that overwrite NODE_HT_header

    bl_space_type = "NODE_EDITOR"

    def draw_network_tree_header(self, context):
        layout = self.layout

        scene = context.scene
        snode = context.space_data
        overlay = snode.overlay
        tool_settings = context.tool_settings

        layout.template_header()

        # Custom node tree is edited as independent ID block
        bl_ui.space_node.NODE_MT_editor_menus.draw_collapsible(context, layout)

        layout.separator_spacer()

        layout.template_ID(scene, "move_network_tree", new="node.new_node_tree")

        # Put pin next to ID block
        layout.prop(snode, "pin", text="", emboss=False)

        layout.operator("sollumz.move_network_editor_state_machine_input")

        layout.separator_spacer()

        layout.operator("node.tree_path_parent", text="", icon='FILE_PARENT')

        # Snap
        row = layout.row(align=True)
        row.prop(tool_settings, "use_snap_node", text="")
        row.prop(tool_settings, "snap_node_element", icon_only=True)
        if tool_settings.snap_node_element != 'GRID':
            row.prop(tool_settings, "snap_target", text="")

        # Overlay toggle & popover
        row = layout.row(align=True)
        row.prop(overlay, "show_overlays", icon='OVERLAY', text="")
        sub = row.row(align=True)
        sub.active = overlay.show_overlays
        sub.popover(panel="NODE_PT_overlay", text="")

    def draw(self, context):
        snode = context.space_data
        if snode.tree_type == NetworkTree.bl_idname:
            self.draw_network_tree_header(context)
        else:
            super(NODE_HT_header, self).draw(context)


def register():
    def move_network_tree_poll(self, node_tree):
        return node_tree.network_tree_type == "ROOT"

    def move_network_tree_update(self, context):
        context.space_data.node_tree = self.move_network_tree
    # TODO: probably not ideal to store current move_network_tree in Scene, but cannot be stored in SpaceNodeEditor
    #  because it does not inherit from ID and we cannot add a PointerProperty to it
    bpy.types.Scene.move_network_tree = bpy.props.PointerProperty(
        type=NetworkTree,
        poll=move_network_tree_poll,
        update=move_network_tree_update
    )

    bpy.utils.register_class(NODE_HT_header)


def unregister():
    bpy.utils.unregister_class(NODE_HT_header)
    del bpy.types.Scene.move_network_tree
