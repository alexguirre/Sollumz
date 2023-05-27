import bpy
from ..cwxml.mrf import MoveParameterizedValueProperty


class MoveNetworkBitProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    bit_position: bpy.props.IntProperty(name="Bit", default=0)


class MoveNetworkProperties(bpy.types.PropertyGroup):
    test: bpy.props.IntProperty(name="Test", default=0)
    triggers: bpy.props.CollectionProperty(
        type=MoveNetworkBitProperties, name="Triggers")
    triggers_ul_index: bpy.props.IntProperty(name="Triggers_UIListIndex", default=0)
    flags: bpy.props.CollectionProperty(
        type=MoveNetworkBitProperties, name="Flags")
    flags_ul_index: bpy.props.IntProperty(name="Flags_UIListIndex", default=0)


class ParameterizedFloatProperty(bpy.types.PropertyGroup):
    use_parameter: bpy.props.BoolProperty(name="Use Parameter", default=False)
    value: bpy.props.FloatProperty(name="Value", default=0.0)
    parameter: bpy.props.StringProperty(name="Parameter", default="")

    def set(self, v: MoveParameterizedValueProperty):
        if v.value is not None:
            self.use_parameter = False
            self.value = float(v.value)
        elif v.parameter:
            self.use_parameter = True
            self.parameter = v.parameter

    def draw(self, name, layout):
        row = layout.row()
        if self.use_parameter:
            row.prop(self, 'parameter', text=name)
        else:
            row.prop(self, 'value', text=name)
        row.prop(self, 'use_parameter', toggle=1, icon='LINKED', icon_only=True)


class ParameterizedBoolProperty(bpy.types.PropertyGroup):
    use_parameter: bpy.props.BoolProperty(name="Use Parameter", default=False)
    value: bpy.props.BoolProperty(name="Value", default=False)
    parameter: bpy.props.StringProperty(name="Parameter", default="")

    def set(self, v: MoveParameterizedValueProperty):
        if v.value is not None:
            self.use_parameter = False
            self.value = bool(v.value)
        elif v.parameter:
            self.use_parameter = True
            self.parameter = v.parameter

    def draw(self, name, layout):
        row = layout.row()
        if self.use_parameter:
            row.prop(self, 'parameter', text=name)
        else:
            row.prop(self, 'value', text=name)
        row.prop(self, 'use_parameter', toggle=1, icon='LINKED', icon_only=True)


def register():
    bpy.types.Object.move_network_properties = bpy.props.PointerProperty(
        type=MoveNetworkProperties)


def unregister():
    del bpy.types.Object.move_network_properties
