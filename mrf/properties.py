import bpy
from ..cwxml.mrf import *


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


ParameterizedValueTypes = [
    ("NONE", "None", "No value", 0),
    ("LITERAL", "Literal", "Specific value", 1),
    ("PARAMETER", "Parameter", "Lookup value in the network parameters", 2),
]


def ParameterizedValueTypeProperty(name=""):
    return bpy.props.EnumProperty(name=name, items=ParameterizedValueTypes)


class ParameterizedFloatProperty(bpy.types.PropertyGroup):
    type: ParameterizedValueTypeProperty(name="Type")
    value: bpy.props.FloatProperty(name="Value", default=0.0)
    parameter: bpy.props.StringProperty(name="Parameter", default="")

    def set(self, v: MoveParameterizedValueProperty):
        if v.value is not None:
            self.type = "LITERAL"
            self.value = float(v.value)
        elif v.parameter:
            self.type = "PARAMETER"
            self.parameter = v.parameter
        else:
            self.type = "NONE"

    def draw(self, name, layout):
        row = layout.row()
        if self.type == "PARAMETER":
            row.prop(self, "parameter", text=name)
        elif self.type == "LITERAL":
            row.prop(self, "value", text=name)
        else:
            row.label(text=name)
        row.prop(self, "type")#, toggle=1, icon='LINKED', icon_only=True)


class ParameterizedBoolProperty(bpy.types.PropertyGroup):
    type: ParameterizedValueTypeProperty(name="Type")
    value: bpy.props.BoolProperty(name="Value", default=False)
    parameter: bpy.props.StringProperty(name="Parameter", default="")

    def set(self, v: MoveParameterizedValueProperty):
        if v.value is not None:
            self.type = "LITERAL"
            self.value = bool(v.value)
        elif v.parameter is not None:
            self.type = "PARAMETER"
            self.parameter = v.parameter
        else:
            self.type = "NONE"

    def draw(self, name, layout):
        row = layout.row()
        if self.type == "PARAMETER":
            row.prop(self, "parameter", text=name)
        elif self.type == "LITERAL":
            row.prop(self, "value", text=name)
        else:
            row.label(text=name)
        row.prop(self, "type")#, , toggle=1, icon='LINKED', icon_only=True)


class ParameterizedAssetProperty(bpy.types.PropertyGroup):
    type: ParameterizedValueTypeProperty(name="Type")
    dictionary_name: bpy.props.StringProperty(name="Dictionary", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    parameter: bpy.props.StringProperty(name="Parameter", default="")

    def set(self, v: MoveParameterizedAssetProperty):
        if v.dictionary_name is not None and v.name is not None:
            self.type = "LITERAL"
            self.dictionary_name = v.dictionary_name
            self.name = v.name
        elif v.parameter is not None:
            self.type = "PARAMETER"
            self.parameter = v.parameter
        else:
            self.type = "NONE"

    def draw(self, name, layout):
        row = layout.row()
        if self.type == "PARAMETER":
            row.prop(self, "parameter", text=name)
            row.prop(self, "type")#, , toggle=1, icon='LINKED', icon_only=True)
        elif self.type == "LITERAL":
            row.label(text=name)
            row.prop(self, "type")#, , toggle=1, icon='LINKED', icon_only=True)
            layout.prop(self, "dictionary_name")
            layout.prop(self, "name")
        else:
            row.label(text=name)
            row.prop(self, "type")# , , toggle=1, icon='LINKED', icon_only=True)


ParameterizedClipContainerTypes = [
    ("VariableClipSet", "VariableClipSet", "VariableClipSet", 0),
    ("ClipSet", "ClipSet", "ClipSet", 1),
    ("ClipDictionary", "ClipDictionary", "ClipDictionary", 2),
    ("Unk3", "Unk3", "Unk3", 3),
]


def ParameterizedClipContainerTypeProperty(name=""):
    return bpy.props.EnumProperty(name=name, items=ParameterizedClipContainerTypes)


class ParameterizedClipProperty(bpy.types.PropertyGroup):
    type: ParameterizedValueTypeProperty(name="Type")
    container_type: ParameterizedClipContainerTypeProperty(name="Container Type")
    container_name: bpy.props.StringProperty(name="Container", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    parameter: bpy.props.StringProperty(name="Parameter", default="")

    def set(self, v: MoveParameterizedClipProperty):
        if v.container_type is not None and v.container_name is not None and v.name is not None:
            self.type = "LITERAL"
            self.container_type = v.container_type
            self.container_name = v.container_name
            self.name = v.name
        elif v.parameter is not None:
            self.type = "PARAMETER"
            self.parameter = v.parameter
        else:
            self.type = "NONE"

    def draw(self, name, layout):
        row = layout.row()
        if self.type == "PARAMETER":
            row.prop(self, "parameter", text=name)
            row.prop(self, "type")#, toggle=1, icon='LINKED', icon_only=True)
        elif self.type == "LITERAL":
            row.label(text=name)
            row.prop(self, "type")#, toggle=1, icon='LINKED', icon_only=True)
            layout.prop(self, "container_type")
            layout.prop(self, "container_name")
            layout.prop(self, "name")
        else:
            row.label(text=name)
            row.prop(self, "type")# , , toggle=1, icon='LINKED', icon_only=True)


#         None = 0, // influence affected by weight (at least in NodeBlend case)
#         Zero = 1, // influence = 0.0
#         One  = 2, // influence = 1.0
InfluenceOverrides = [
    ("None", "None", "None", 0),
    ("Zero", "Zero", "Zero", 1),
    ("One", "One", "One", 2),
]


def InfluenceOverrideProperty(name=""):
    return bpy.props.EnumProperty(name=name, items=InfluenceOverrides)


WeightModifierTypes = [
    ("SlowInSlowOut", "SlowInSlowOut", "SlowInSlowOut", 0),
    ("SlowOut", "SlowOut", "SlowOut", 1),
    ("SlowIn", "SlowIn", "SlowIn", 2),
    ("None", "None", "None", 3),
]


def WeightModifierTypeProperty(name=""):
    return bpy.props.EnumProperty(name=name, items=WeightModifierTypes)


SynchronizerTypes = [
    ("Phase", "Phase", "Phase", 0),
    ("Tag", "Tag", "Tag", 1),
    ("None", "None", "None", 2),
]


def SynchronizerTypeProperty(name=""):
    return bpy.props.EnumProperty(name=name, items=SynchronizerTypes)


class ATNodeNChildProperties(bpy.types.PropertyGroup):
    weight: bpy.props.PointerProperty(name="Weight", type=ParameterizedFloatProperty)
    frame_filter: bpy.props.PointerProperty(name="Frame Filter", type=ParameterizedAssetProperty)

    def set(self, v: MoveNodeNChildren.Child):
        self.weight.set(v.weight)
        self.frame_filter.set(v.frame_filter)


SMConditionTypes = [
    ("ParameterInsideRange", "ParameterInsideRange", "ParameterInsideRange", 0),
    ("ParameterOutsideRange", "ParameterOutsideRange", "ParameterOutsideRange", 1),
    ("MoveNetworkTrigger", "MoveNetworkTrigger", "MoveNetworkTrigger", 2),
    ("MoveNetworkFlag", "MoveNetworkFlag", "MoveNetworkFlag", 3),
    ("ParameterGreaterThan", "ParameterGreaterThan", "ParameterGreaterThan", 4),
    ("ParameterGreaterOrEqual", "ParameterGreaterOrEqual", "ParameterGreaterOrEqual", 5),
    ("ParameterLessThan", "ParameterLessThan", "ParameterLessThan", 6),
    ("ParameterLessOrEqual", "ParameterLessOrEqual", "ParameterLessOrEqual", 7),
    ("TimeGreaterThan", "TimeGreaterThan", "TimeGreaterThan", 8),
    ("TimeLessThan", "TimeLessThan", "TimeLessThan", 9),
    ("EventOccurred", "EventOccurred", "EventOccurred", 10),
    ("BoolParameterExists", "BoolParameterExists", "BoolParameterExists", 11),
    ("BoolParameterEquals", "BoolParameterEquals", "BoolParameterEquals", 12),
]


class SMConditionProperties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(name="Type", items=SMConditionTypes)
    parameter: bpy.props.StringProperty(name="Parameter", default="")
    value_bool: bpy.props.BoolProperty(name="Value", default=False)
    value_float: bpy.props.FloatProperty(name="Value", default=0.0)
    min: bpy.props.FloatProperty(name="Min", default=0.0)
    max: bpy.props.FloatProperty(name="Max", default=0.0)
    bit_position: bpy.props.IntProperty(name="Bit Position", default=0)  # TODO: should just use the flag/trigger name here

    def set(self, v: MoveConditionBase):
        self.type = v.type
        if self.type in {"ParameterInsideRange", "ParameterOutsideRange"}:
            self.parameter = v.parameter
            self.min = v.min
            self.max = v.max
        elif self.type in {"ParameterGreaterThan", "ParameterGreaterOrEqual", "ParameterLessThan", "ParameterLessOrEqual"}:
            self.parameter = v.parameter
            self.value_float = v.value
        elif self.type in {"TimeGreaterThan", "TimeLessThan"}:
            self.value_float = v.value
        elif self.type in {"MoveNetworkTrigger", "MoveNetworkFlag"}:
            self.bit_position = v.bit_position
            self.value_bool = v.invert
        elif self.type in {"EventOccurred", "BoolParameterExists", "BoolParameterEquals"}:
            self.parameter = v.parameter
            self.value_bool = v.value

    def draw(self, layout):
        layout.prop(self, "type")
        if self.type in {"ParameterInsideRange", "ParameterOutsideRange"}:
            layout.prop(self, "parameter")
            row = layout.row()
            row.prop(self, "min")
            row.prop(self, "max")
        elif self.type in {"ParameterGreaterThan", "ParameterGreaterOrEqual", "ParameterLessThan", "ParameterLessOrEqual"}:
            layout.prop(self, "parameter")
            layout.prop(self, "value_float")
        elif self.type in {"TimeGreaterThan", "TimeLessThan"}:
            layout.prop(self, "value_float")
        elif self.type in {"MoveNetworkTrigger", "MoveNetworkFlag"}:
            layout.prop(self, "bit_position")
            layout.prop(self, "value_bool", text="Invert")
        elif self.type in {"EventOccurred"}:
            layout.prop(self, "parameter", text="Event")
            layout.prop(self, "value_bool", text="Invert")
        elif self.type in {"BoolParameterExists"}:
            layout.prop(self, "parameter")
            layout.prop(self, "value_bool", text="Invert")
        elif self.type in {"BoolParameterEquals"}:
            layout.prop(self, "parameter")
            layout.prop(self, "value_bool")


class SMTransitionProperties(bpy.types.PropertyGroup):
    target_state: bpy.props.StringProperty(name="Target State", default="")
    duration: bpy.props.FloatProperty(name="Duration", default=0.0)
    duration_parameter_name: bpy.props.StringProperty(name="Duration Parameter Name", default="")
    progress_parameter_name: bpy.props.StringProperty(name="Progress Parameter Name", default="")
    blend_modifier: WeightModifierTypeProperty(name="Blend Modifier")
    synchronizer_type: SynchronizerTypeProperty(name="Synchronizer Type")
    synchronizer_tag_flags: bpy.props.StringProperty(name="Synchronizer Tag Flags", default="")
    frame_filter: bpy.props.PointerProperty(name='Frame Filter', type=ParameterizedAssetProperty)
    unk_flag2_detach_update_observers: bpy.props.BoolProperty(name="Unk Flag 2 Detach Update Observers", default=False)
    unk_flag18: bpy.props.BoolProperty(name="Unk Flag 18", default=False)
    unk_flag19: bpy.props.BoolProperty(name="Unk Flag 19", default=False)
    conditions: bpy.props.CollectionProperty(name="Conditions", type=SMConditionProperties)

    ui_from: bpy.props.FloatVectorProperty(default=(0.0, 0.0), size=2)
    ui_to: bpy.props.FloatVectorProperty(default=(0.0, 0.0), size=2)
    ui_hovered: bpy.props.BoolProperty(default=False, update=lambda s, c: c.region.tag_redraw())
    ui_active: bpy.props.BoolProperty(default=False, update=lambda s, c: c.region.tag_redraw())
    ui_active_condition_index: bpy.props.IntProperty()

    def set(self, v: MoveStateTransition):
        self.duration = v.duration
        self.duration_parameter_name = v.duration_parameter_name
        self.progress_parameter_name = v.progress_parameter_name
        self.blend_modifier = v.blend_modifier or "None"
        self.synchronizer_type = v.synchronizer_type or "None"
        self.synchronizer_tag_flags = v.synchronizer_tag_flags
        self.frame_filter.set(v.frame_filter)
        self.unk_flag2_detach_update_observers = v.unk_flag2_detach_update_observers
        self.unk_flag18 = v.unk_flag18
        self.unk_flag19 = v.unk_flag19
        self.conditions.clear()
        for c in v.conditions:
            self.conditions.add().set(c)


def register():
    pass
    # bpy.types.Object.move_network_properties = bpy.props.PointerProperty(
    #     type=MoveNetworkProperties)


def unregister():
    pass
    # del bpy.types.Object.move_network_properties
