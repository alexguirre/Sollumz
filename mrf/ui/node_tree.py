import bpy
import bl_ui
import math
import mathutils
import gpu
from gpu_extras.batch import batch_for_shader

NetworkTreeTypes = [
    ("ROOT", "Root", "Root tree", 0),
    ("ANIMATION_TREE", "Animation Tree", "Animation tree", 1),
    ("STATE_MACHINE", "State Machine", "State machine transition graph", 2),
]


class NetworkTree(bpy.types.NodeTree):
    bl_idname = "SOLLUMZ_NT_MOVE_NETWORK_NetworkTree"
    bl_label = "MoVE Network Editor"
    bl_icon = "ONIONSKIN_ON"

    network_tree_type: bpy.props.EnumProperty(name="Type", items=NetworkTreeTypes)
    network_root: bpy.props.PointerProperty(name="Network Root", type=bpy.types.NodeTree)


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


shader = gpu.shader.from_builtin('SMOOTH_COLOR')


def _get_node_pos(node):
    x = node.location.x
    y = node.location.y
    parent = node.parent
    while parent is not None:
        x += parent.location.x
        y += parent.location.y
        parent = parent.parent
    return x, y


def calc_transition_arrow(node_from, node_to):
    margin = 5

    def _get_corner(left, right, top, bottom, corner_id):
        if corner_id == 0:  # top-left
            return mathutils.Vector((left, top))
            # return mathutils.Vector((pos.x - margin, pos.y + margin))
        if corner_id == 1:  # top-right
            return mathutils.Vector((right, top))
            # return mathutils.Vector((pos.x + size.x + margin, pos.y + margin))
        if corner_id == 2:  # bottom-left
            return mathutils.Vector((left, bottom))
            # return mathutils.Vector((pos.x - margin, pos.y - size.y - margin))
        if corner_id == 3:  # bottom-right
            return mathutils.Vector((right, bottom))
            # return mathutils.Vector((pos.x + size.x + margin, pos.y - size.y - margin))
        raise ValueError("Invalid corner_id: %d" % corner_id)

    vfrom = node_from.location
    vfrom_size = node_from.dimensions
    vfrom_left_x = vfrom.x - margin
    vfrom_right_x = vfrom.x + vfrom_size.x + margin
    vfrom_top_y = vfrom.y + margin
    vfrom_bottom_y = vfrom.y - vfrom_size.y - margin

    vto = node_to.location
    vto_size = node_to.dimensions
    vto_left_x = vto.x - margin
    vto_right_x = vto.x + vto_size.x + margin
    vto_top_y = vto.y + margin
    vto_bottom_y = vto.y - vto_size.y - margin

    # check if any side is aligned
    if vfrom_top_y < vto_bottom_y and vfrom_left_x <= vto_right_x and vto_left_x <= vfrom_right_x:  # top
        arrow_x = (max(vfrom_left_x, vto_left_x) + min(vfrom_right_x, vto_right_x)) / 2
        return mathutils.Vector((arrow_x, vfrom_top_y)), mathutils.Vector((arrow_x, vto_bottom_y))
    elif vfrom_bottom_y > vto_top_y and vfrom_left_x <= vto_right_x and vto_left_x <= vfrom_right_x:  # bottom
        arrow_x = (max(vfrom_left_x, vto_left_x) + min(vfrom_right_x, vto_right_x)) / 2
        return mathutils.Vector((arrow_x, vfrom_bottom_y)), mathutils.Vector((arrow_x, vto_top_y))
    elif vfrom_left_x > vto_right_x and vfrom_top_y >= vto_bottom_y and vto_top_y >= vfrom_bottom_y:  # left
        arrow_y = (max(vfrom_bottom_y, vto_bottom_y) + min(vfrom_top_y, vto_top_y)) / 2
        return mathutils.Vector((vfrom_left_x, arrow_y)), mathutils.Vector((vto_right_x, arrow_y))
    elif vfrom_right_x < vto_left_x and vfrom_top_y >= vto_bottom_y and vto_top_y >= vfrom_bottom_y:  # right
        arrow_y = (max(vfrom_bottom_y, vto_bottom_y) + min(vfrom_top_y, vto_top_y)) / 2
        return mathutils.Vector((vfrom_right_x, arrow_y)), mathutils.Vector((vto_left_x, arrow_y))

    # no side is aligned, connect from the closest corners
    from_corners = [_get_corner(vfrom_left_x, vfrom_right_x, vfrom_top_y, vfrom_bottom_y, i) for i in range(4)]
    to_corners = [_get_corner(vto_left_x, vto_right_x, vto_top_y, vto_bottom_y, i) for i in range(4)]

    closest_corners = None
    closest_corners_dist = float("inf")
    for from_corner in from_corners:
        for to_corner in to_corners:
            dist = (from_corner - to_corner).length_squared
            if dist < closest_corners_dist:
                closest_corners_dist = dist
                closest_corners = (from_corner, to_corner)

    return closest_corners


def draw_transition_arrows(pos_pairs):
    # source_color = (0.1, 0.1, 0.7, 1)
    # target_color = (0.2, 0.8, 0.1, 1)
    source_color = (0.85, 0.85, 0.85, 1)
    target_color = (0.85, 0.85, 0.85, 1)
    rot1 = mathutils.Matrix.Rotation(math.pi * 0.1, 2)
    rot2 = mathutils.Matrix.Rotation(-math.pi * 0.1, 2)
    for vfrom, vto in pos_pairs:
        vdir1 = (vfrom - vto).normalized()
        vdir2 = (vfrom - vto).normalized()
        vdir1.rotate(rot1)
        vdir2.rotate(rot2)
        arrow_tip1 = vto + vdir1 * 30
        arrow_tip2 = vto + vdir2 * 30

        coords = [
            (vfrom.x, vfrom.y, 0), (vto.x, vto.y, 0),
            (vto.x, vto.y, 0), (arrow_tip1.x, arrow_tip1.y, 0),
            (vto.x, vto.y, 0), (arrow_tip2.x, arrow_tip2.y, 0)
        ]
        colors = [
            source_color, target_color,
            target_color, target_color,
            target_color, target_color
        ]
        batch = batch_for_shader(shader, 'LINES', {"pos": coords, "color": colors})
        # shader.uniform_float("color", (1, 1, 0, 1))
        gpu.state.line_width_set(3)
        batch.draw(shader)


def fix_transition_arrows_overlaps(pos_pairs):
    fixed = set()
    for i in range(len(pos_pairs)):
        if i in fixed:
            continue

        vfrom1, vto1 = pos_pairs[i]
        overlaps = []
        for j in range(len(pos_pairs)):
            if i == j or j in fixed:
                continue
            vfrom2, vto2 = pos_pairs[j]
            if (vfrom1 == vfrom1 and vto1 == vto2) or (vfrom1 == vto2 and vto1 == vfrom2):
                overlaps.append(j)
                fixed.add(i)
                fixed.add(j)

        if len(overlaps) > 1:
            # raise Exception("States can have more than one transition to the same state!")
            continue

        if len(overlaps) == 0:
            continue

        j = overlaps[0]
        vfrom2, vto2 = pos_pairs[j]
        perp = (vto1 - vfrom1).normalized().orthogonal()
        pos_pairs[i] = (vfrom1 + perp * 7, vto1 + perp * 7)
        pos_pairs[j] = (vfrom2 - perp * 7, vto2 - perp * 7)


def draw_node_editor_background():
    space = bpy.context.space_data
    if space.tree_type != NetworkTree.bl_idname:
        return

    node_tree = space.edit_tree
    if node_tree is None or node_tree.network_tree_type not in {"ROOT", "STATE_MACHINE"}:
        return

    transition_arrows = []
    for node in node_tree.nodes:
        if node.bl_idname == "SOLLUMZ_NT_MOVE_NETWORK_SMNodeStart":
            start_node = node_tree.nodes[node.start_state]
            transition_arrows.append(calc_transition_arrow(node, start_node))
        else:
            for t in node.transitions:
                target_node = node_tree.nodes[t.target_state]
                transition_arrows.append(calc_transition_arrow(node, target_node))

    fix_transition_arrows_overlaps(transition_arrows)
    draw_transition_arrows(transition_arrows)


class NODE_HT_header(bl_ui.space_node.NODE_HT_header):
    """
    Overwrite the header of the node editor.
    Mainly to limit the tree selection to root MoVE network trees.
    """
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


def move_network_tree_poll(self, node_tree):
    return node_tree.network_tree_type == "ROOT"


def move_network_tree_update(self, context):
    context.space_data.node_tree = self.move_network_tree


def register():
    # TODO: probably not ideal to store current move_network_tree in Scene, but cannot be stored in SpaceNodeEditor
    #  because it does not inherit from ID and we cannot add a PointerProperty to it
    bpy.types.Scene.move_network_tree = bpy.props.PointerProperty(
        type=NetworkTree,
        poll=move_network_tree_poll,
        update=move_network_tree_update
    )

    bpy.utils.register_class(NODE_HT_header)
    # TODO: unregister draw_handler
    bpy.types.SpaceNodeEditor.draw_handler_add(draw_node_editor_background, (), 'WINDOW', 'POST_VIEW')