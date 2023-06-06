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
    container_type: bpy.props.EnumProperty(name="Container Type", items=[
        ("VariableClipSet", "VariableClipSet", "VariableClipSet", 0),
        ("ClipSet", "ClipSet", "ClipSet", 1),
        ("ClipDictionary", "ClipDictionary", "ClipDictionary", 2),
        ("Unk3", "Unk3", "Unk3", 3),
    ])
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


WeightModifierTypes = [
    ("SlowInSlowOut", "SlowInSlowOut", "SlowInSlowOut", 0),
    ("SlowOut", "SlowOut", "SlowOut", 1),
    ("SlowIn", "SlowIn", "SlowIn", 2),
    ("None", "None", "None", 3),
]


SynchronizerTypes = [
    ("Phase", "Phase", "Phase", 0),
    ("Tag", "Tag", "Tag", 1),
    ("None", "None", "None", 2),
]

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
    blend_modifier: bpy.props.EnumProperty(name="Blend Modifier", items=WeightModifierTypes)
    synchronizer_type: bpy.props.EnumProperty(name="Synchronizer Type", items=SynchronizerTypes)
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

    # self.duration = ValueProperty("Duration", 0.0)
    # self.duration_parameter_name = TextPropertyRequired("DurationParameterName")
    # self.progress_parameter_name = TextPropertyRequired("ProgressParameterName")
    # self.blend_modifier = TextPropertyRequired("BlendModifier")
    # self.synchronizer_type = TextPropertyRequired("SynchronizerType")
    # self.synchronizer_tag_flags = TextProperty("SynchronizerTagFlags")
    # self.frame_filter = MoveParameterizedAssetProperty("FrameFilter")  # note: cannot actually use parameters here
    # self.unk_flag2_detach_update_observers = ValueProperty("UnkFlag2_DetachUpdateObservers", False)
    # self.unk_flag18 = ValueProperty("UnkFlag18", False)
    # self.unk_flag19 = ValueProperty("UnkFlag19", False)
    # self.conditions = MoveConditionsList()

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
