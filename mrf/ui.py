import bpy
from ..sollumz_ui import SOLLUMZ_PT_OBJECT_PANEL
from ..sollumz_properties import SollumType


class SOLLUMZ_UL_MOVE_NETWORK_BITS_LIST(bpy.types.UIList):
    bl_idname = "SOLLUMZ_UL_MOVE_NETWORK_BITS_LIST"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "bit_position", text=item.name)


def draw_move_network_properties(self, context):
    obj = context.active_object
    if obj.sollum_type == SollumType.MOVE_NETWORK:
        self.layout.label(text="Triggers")
        self.layout.template_list(SOLLUMZ_UL_MOVE_NETWORK_BITS_LIST.bl_idname, "Triggers",
                                  obj.move_network_properties, "triggers",
                                  obj.move_network_properties, "triggers_ul_index")
        self.layout.label(text="Flags")
        self.layout.template_list(SOLLUMZ_UL_MOVE_NETWORK_BITS_LIST.bl_idname, "Flags",
                                  obj.move_network_properties, "flags",
                                  obj.move_network_properties, "flags_ul_index")
        for prop in obj.move_network_properties.__annotations__:
            if prop not in {"flags", "triggers"}:
                self.layout.prop(obj.move_network_properties, prop)


def register():
    SOLLUMZ_PT_OBJECT_PANEL.append(draw_move_network_properties)


def unregister():
    SOLLUMZ_PT_OBJECT_PANEL.remove(draw_move_network_properties)
