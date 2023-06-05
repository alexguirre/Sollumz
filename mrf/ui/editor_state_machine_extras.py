import bpy
import mathutils
import gpu
from gpu_extras.batch import batch_for_shader
import math
from ..nodes.node_tree import NetworkTree


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
        if corner_id == 1:  # top-right
            return mathutils.Vector((right, top))
        if corner_id == 2:  # bottom-left
            return mathutils.Vector((left, bottom))
        if corner_id == 3:  # bottom-right
            return mathutils.Vector((right, bottom))
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


def draw_transition_arrows(pos_pairs, hovered_idx, active_idx):
    # source_color = (0.1, 0.1, 0.7, 1)
    # target_color = (0.2, 0.8, 0.1, 1)
    source_color = (0.85, 0.85, 0.85, 1)
    target_color = (0.85, 0.85, 0.85, 1)
    hovered_color = (0.85, 0.35, 0.35, 1)
    active_color = (0.35, 0.35, 0.85, 1)
    rot1 = mathutils.Matrix.Rotation(math.pi * 0.1, 2)
    rot2 = mathutils.Matrix.Rotation(-math.pi * 0.1, 2)
    i = 0
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
        if i == hovered_idx:
            colors = [
                hovered_color, hovered_color,
                hovered_color, hovered_color,
                hovered_color, hovered_color
            ]
        elif i == active_idx:
            colors = [
                active_color, active_color,
                active_color, active_color,
                active_color, active_color
            ]
        else:
            colors = [
                source_color, target_color,
                target_color, target_color,
                target_color, target_color
            ]
        batch = batch_for_shader(shader, 'LINES', {"pos": coords, "color": colors})
        # shader.uniform_float("color", (1, 1, 0, 1))
        gpu.state.line_width_set(3)
        batch.draw(shader)

        i += 1


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


def draw_state_machine_transitions():
    space = bpy.context.space_data
    if space.tree_type != NetworkTree.bl_idname:
        return

    node_tree = space.edit_tree
    if node_tree is None or node_tree.network_tree_type not in {"ROOT", "STATE_MACHINE"}:
        return

    transition_arrows = []
    hovered_idx = None
    active_idx = None
    for node in node_tree.nodes:
        if node.bl_idname == "SOLLUMZ_NT_MOVE_NETWORK_SMNodeStart":
            start_node = node_tree.nodes[node.start_state]
            transition_arrows.append(calc_transition_arrow(node, start_node))
        else:
            for t in node.transitions:
                target_node = node_tree.nodes[t.target_state]
                arrow = calc_transition_arrow(node, target_node)
                t.ui_from = arrow[0]
                t.ui_to = arrow[1]
                if t.ui_hovered:
                    hovered_idx = len(transition_arrows)
                if t.ui_active:
                    active_idx = len(transition_arrows)
                transition_arrows.append(arrow)

    fix_transition_arrows_overlaps(transition_arrows)
    draw_transition_arrows(transition_arrows, hovered_idx, active_idx)


draw_state_machine_transitions_handle = None


def register():
    global draw_state_machine_transitions_handle
    draw_state_machine_transitions_handle = bpy.types.SpaceNodeEditor.draw_handler_add(draw_state_machine_transitions, (), 'WINDOW', 'POST_VIEW')


def unregister():
    global draw_state_machine_transitions_handle
    if draw_state_machine_transitions_handle is not None:
        bpy.types.SpaceNodeEditor.draw_handler_remove(draw_state_machine_transitions_handle, 'WINDOW')
        draw_state_machine_transitions_handle = None
