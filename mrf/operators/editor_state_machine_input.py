import bpy
import mathutils
from ..nodes.node_tree import NetworkTree


class SOLLUMZ_OT_MOVE_NETWORK_editor_state_machine_input(bpy.types.Operator):
    bl_idname = "sollumz.move_network_editor_state_machine_input"
    bl_label = "State Machine Input Operator"
    bl_action = bl_label

    # @classmethod
    # def poll(cls, context):
    #     return (context.space_data.type == "NODE_EDITOR" and
    #             context.space_data.tree_type == NetworkTree.bl_idname and
    #             context.space_data.edit_tree is not None and
    #             context.space_data.edit_tree.bl_idname == NetworkTree.bl_idname)

    def modal(self, context, event: bpy.types.Event):
        # print(">>> modal '%s' '%s' (%s, %s) (%s, %s)" % (context.area, context.region, event.mouse_x, event.mouse_y, event.mouse_region_x, event.mouse_region_y))

        # context.region.tag_redraw()

        region = context.region
        if (event.mouse_region_x < 0 or event.mouse_region_x > region.width or
            event.mouse_region_y < 0 or event.mouse_region_y > region.height):
            return {"PASS_THROUGH"}

        space = context.space_data
        if space.tree_type != NetworkTree.bl_idname:
            return {"PASS_THROUGH"}

        node_tree = space.edit_tree
        if node_tree is None or node_tree.network_tree_type not in {"ROOT", "STATE_MACHINE"}:
            return {"PASS_THROUGH"}

        ui_scale = context.preferences.system.ui_scale
        x, y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
        x, y = x / ui_scale, y / ui_scale

        pos = mathutils.Vector((x, y))

        for node in node_tree.nodes:
            if node.bl_idname == "SOLLUMZ_NT_MOVE_NETWORK_SMNodeStart":
                pass
            else:
                for t in node.transitions:
                    intersection = mathutils.geometry.intersect_line_sphere_2d(t.ui_from, t.ui_to, pos, 10)
                    t.ui_hovered = intersection[0] is not None

        # print(event.type, event.value)
        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            node_selected = False
            for node in node_tree.nodes:
                if node.bl_idname == "SOLLUMZ_NT_MOVE_NETWORK_SMNodeStart":
                    pass
                else:
                    i = 0
                    for t in node.transitions:
                        t.ui_active = not node_selected and t.ui_hovered
                        if t.ui_active:
                            node_tree.ui_active_transition_source_node_name = node.name
                            node_tree.ui_active_transition_index = i
                            node_selected = True
                        i += 1

            if not node_selected:
                node_tree.ui_active_transition_source_node_name = ""

        # context.region.tag_redraw()
        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        # print(">>> invoke %s" % event)
        # self.init_loc_x = context.object.location.x
        # self.value = event.mouse_x
        # self.execute(context)

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL", "PASS_THROUGH"}
