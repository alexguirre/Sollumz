import bpy


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


def register():
    bpy.types.Object.move_network_properties = bpy.props.PointerProperty(
        type=MoveNetworkProperties)


def unregister():
    del bpy.types.Object.move_network_properties
