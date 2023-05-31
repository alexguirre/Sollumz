import bpy
import math
import mathutils
import gpu
from gpu_extras.batch import batch_for_shader


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
    margin = 10

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
    source_color = (0.1, 0.1, 0.7, 1)
    target_color = (0.2, 0.8, 0.1, 1)
    rot1 = mathutils.Matrix.Rotation(math.pi * 0.175, 2)
    rot2 = mathutils.Matrix.Rotation(-math.pi * 0.175, 2)
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
        gpu.state.line_width_set(5)
        batch.draw(shader)


def draw_node_editor_background():

    node_tree = bpy.context.space_data.edit_tree
    if node_tree is None:
        return

    transition_arrows = []
    for node in node_tree.nodes:
        if node.bl_idname != "SOLLUMZ_NT_MOVE_NETWORK_NodeState_New":
            continue

        for t in node.transitions:
            target_node = node_tree.nodes[t.target_state]
            transition_arrows.append(calc_transition_arrow(node, target_node))

    draw_transition_arrows(transition_arrows)


def register():
    # TODO: unregister draw_handler
    bpy.types.SpaceNodeEditor.draw_handler_add(draw_node_editor_background, (), 'WINDOW', 'POST_VIEW')