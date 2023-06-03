import bpy
from ..cwxml.mrf import MoveParameterizedValueProperty, MoveParameterizedAssetProperty, MoveParameterizedClipProperty


# class MoveNetworkBitProperties(bpy.types.PropertyGroup):
#     name: bpy.props.StringProperty(name="Name")
#     bit_position: bpy.props.IntProperty(name="Bit", default=0)
#
#
# class MoveNetworkProperties(bpy.types.PropertyGroup):
#     test: bpy.props.IntProperty(name="Test", default=0)
#     triggers: bpy.props.CollectionProperty(
#         type=MoveNetworkBitProperties, name="Triggers")
#     triggers_ul_index: bpy.props.IntProperty(name="Triggers_UIListIndex", default=0)
#     flags: bpy.props.CollectionProperty(
#         type=MoveNetworkBitProperties, name="Flags")
#     flags_ul_index: bpy.props.IntProperty(name="Flags_UIListIndex", default=0)


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
        elif v.parameter is not None:
            self.use_parameter = True
            self.parameter = v.parameter

    def draw(self, name, layout):
        row = layout.row()
        if self.use_parameter:
            row.prop(self, 'parameter', text=name)
        else:
            row.prop(self, 'value', text=name)
        row.prop(self, 'use_parameter', toggle=1, icon='LINKED', icon_only=True)


class ParameterizedAssetProperty(bpy.types.PropertyGroup):
    use_parameter: bpy.props.BoolProperty(name="Use Parameter", default=False)
    dictionary_name: bpy.props.StringProperty(name="Dictionary", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    parameter: bpy.props.StringProperty(name="Parameter", default="")

    def set(self, v: MoveParameterizedAssetProperty):
        if v.dictionary_name is not None and v.name is not None:
            self.use_parameter = False
            self.dictionary_name = v.dictionary_name
            self.name = v.name
        elif v.parameter is not None:
            self.use_parameter = True
            self.parameter = v.parameter

    def draw(self, name, layout):
        if self.use_parameter:
            row = layout.row()
            row.prop(self, 'parameter', text=name)
            row.prop(self, 'use_parameter', toggle=1, icon='LINKED', icon_only=True)
        else:
            row = layout.row()
            row.label(text=name)
            row.prop(self, 'use_parameter', toggle=1, icon='LINKED', icon_only=True)
            layout.prop(self, 'dictionary_name', text="Dictionary")
            layout.prop(self, 'name', text="Name")


class ParameterizedClipProperty(bpy.types.PropertyGroup):
    use_parameter: bpy.props.BoolProperty(name="Use Parameter", default=False)
    container_type: bpy.props.StringProperty(name="Container Type", default="")
    container_name: bpy.props.StringProperty(name="Container", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    parameter: bpy.props.StringProperty(name="Parameter", default="")

    def set(self, v: MoveParameterizedClipProperty):
        if v.container_type is not None and v.container_name is not None and v.name is not None:
            self.use_parameter = False
            self.container_type = v.container_type
            self.container_name = v.container_name
            self.name = v.name
        elif v.parameter is not None:
            self.use_parameter = True
            self.parameter = v.parameter

    def draw(self, name, layout):
        if self.use_parameter:
            row = layout.row()
            row.prop(self, 'parameter', text=name)
            row.prop(self, 'use_parameter', toggle=1, icon='LINKED', icon_only=True)
        else:
            row = layout.row()
            row.label(text=name)
            row.prop(self, 'use_parameter', toggle=1, icon='LINKED', icon_only=True)
            layout.prop(self, 'container_type', text="Container Type")
            layout.prop(self, 'container_name', text="Container")
            layout.prop(self, 'name', text="Name")


class SMTransitionProperties(bpy.types.PropertyGroup):
    target_state: bpy.props.StringProperty(name="Target State", default="")


def register():
    pass
    # bpy.types.Object.move_network_properties = bpy.props.PointerProperty(
    #     type=MoveNetworkProperties)


def unregister():
    pass
    # del bpy.types.Object.move_network_properties
