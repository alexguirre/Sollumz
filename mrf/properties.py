import bpy
from ..cwxml.mrf import *
from ..sollumz_properties import SollumType


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
    ("NONE", "None", "No value", "REMOVE", 0),
    ("LITERAL", "Literal", "Specific value", "UNLINKED", 1),
    ("PARAMETER", "Parameter", "Lookup value in the network parameters", "LINKED", 2),
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

    def draw(self, name, context, layout):
        network = context.space_data.edit_tree
        network = network.network_root or network
        row = layout.row()
        if self.type == "PARAMETER":
            row.prop_search(self, "parameter", network.network_parameters, "parameters_float", text=name)
        elif self.type == "LITERAL":
            row.prop(self, "value", text=name)
        else:
            row.label(text=name)
        row.prop(self, "type", text="", icon_only=True, expand=True)


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

    def draw(self, name, context, layout):
        network = context.space_data.edit_tree
        network = network.network_root or network
        row = layout.row()
        if self.type == "PARAMETER":
            row.prop_search(self, "parameter", network.network_parameters, "parameters_bool", text=name)
        elif self.type == "LITERAL":
            row.prop(self, "value", text=name)
        else:
            row.label(text=name)
        row.prop(self, "type", text="", icon_only=True, expand=True)


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

    def draw(self, name, context, layout):
        network = context.space_data.edit_tree
        network = network.network_root or network
        row = layout.row()
        if self.type == "PARAMETER":
            row.prop_search(self, "parameter", network.network_parameters, "parameters_asset", text=name)
            row.prop(self, "type", text="", icon_only=True, expand=True)
        elif self.type == "LITERAL":
            row.label(text=name)
            row.prop(self, "type", text="", icon_only=True, expand=True)
            layout.prop(self, "dictionary_name")
            layout.prop(self, "name")
        else:
            row.label(text=name)
            row.prop(self, "type", text="", icon_only=True, expand=True)


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

    def draw(self, name, context, layout):
        network = context.space_data.edit_tree
        network = network.network_root or network
        row = layout.row()
        if self.type == "PARAMETER":
            row.prop_search(self, "parameter", network.network_parameters, "parameters_clip", text=name)
            row.prop(self, "type", text="", icon_only=True, expand=True)
        elif self.type == "LITERAL":
            row.label(text=name)
            row.prop(self, "type", text="", icon_only=True, expand=True)
            layout.prop(self, "container_type")
            layout.prop(self, "container_name")
            layout.prop(self, "name")
        else:
            row.label(text=name)
            row.prop(self, "type", text="", icon_only=True, expand=True)


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
    ("None", "None", "None", 0),
    ("Phase", "Phase", "Phase", 1),
    ("Tag", "Tag", "Tag", 2),
]


def SynchronizerTypeProperty(name=""):
    return bpy.props.EnumProperty(name=name, items=SynchronizerTypes)


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


class NetworkParameterFloat(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
    value: bpy.props.FloatProperty(name="Value", default=0.0)


class NetworkParameterBool(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
    value: bpy.props.BoolProperty(name="Value", default=False)


class NetworkParameterClip(bpy.types.PropertyGroup):
    def poll_clip_dictionaries(self, obj):
        return obj.sollum_type == SollumType.CLIP_DICTIONARY

    def poll_clips(self, obj):
        return (self.clip_dictionary is not None and
                obj.sollum_type == SollumType.CLIP and
                obj.parent is not None and
                self.clip_dictionary == obj.parent.parent)

    def on_clip_dictionary_update(self, context):
        # clear the clip field when the clip dictionary is changed
        if self.clip_dictionary != self.prev_clip_dictionary:
            self.clip = None
        self.prev_clip_dictionary = self.clip_dictionary

    name: bpy.props.StringProperty(name="Name", default="")
    clip_dictionary: bpy.props.PointerProperty(name="Clip Dictionary", type=bpy.types.Object,
                                               poll=poll_clip_dictionaries, update=on_clip_dictionary_update)
    clip: bpy.props.PointerProperty(name="Clip", type=bpy.types.Object, poll=poll_clips)

    # used to detect when the clip dictionary is changed
    prev_clip_dictionary: bpy.props.PointerProperty(type=bpy.types.Object)

    @property
    def value(self):
        return self.clip

    @value.setter
    def value(self, value):
        if value is None:
            self.clip = None
            self.clip_dictionary = None
            return

        assert value.sollum_type == SollumType.CLIP
        self.clip_dictionary = value.parent.parent
        self.clip = value


class NetworkParameterAsset(bpy.types.PropertyGroup):  # TODO: may need more specific type (expressions, frame filters, etc.)
    name: bpy.props.StringProperty(name="Name", default="")
    value: bpy.props.StringProperty(name="Value", default="")


class NetworkParameters(bpy.types.PropertyGroup):
    parameters_float: bpy.props.CollectionProperty(name="Float Parameters", type=NetworkParameterFloat)
    parameters_bool: bpy.props.CollectionProperty(name="Bool Parameters", type=NetworkParameterBool)
    parameters_clip: bpy.props.CollectionProperty(name="Clip Parameters", type=NetworkParameterClip)
    parameters_asset: bpy.props.CollectionProperty(name="Asset Parameters", type=NetworkParameterAsset)

    def exists(self, parameter_name):
        for collection in (self.parameters_float, self.parameters_bool, self.parameters_clip, self.parameters_asset):
            if collection.find(parameter_name) != -1:
                return True
        return False

    def remove(self, parameter_name):
        for collection in (self.parameters_float, self.parameters_bool, self.parameters_clip, self.parameters_asset):
            i = collection.find(parameter_name)
            if i != -1:
                collection.remove(i)
                return

    def clear(self):
        self.parameters_float.clear()
        self.parameters_bool.clear()
        self.parameters_clip.clear()
        self.parameters_asset.clear()

    def try_add(self, parameter_name, data_type):
        if data_type == "float":
            return self.try_add_float(parameter_name)
        elif data_type == "bool":
            return self.try_add_bool(parameter_name)
        elif data_type == "clip":
            return self.try_add_clip(parameter_name)
        elif data_type == "asset":
            return self.try_add_asset(parameter_name)
        else:
            raise Exception(f"Unknown data type: {data_type}")

    def try_add_float(self, parameter_name):
        if self.exists(parameter_name):
            return False
        self.parameters_float.add().name = parameter_name
        return True

    def try_add_bool(self, parameter_name):
        if self.exists(parameter_name):
            return False
        self.parameters_bool.add().name = parameter_name
        return True

    def try_add_clip(self, parameter_name):
        if self.exists(parameter_name):
            return False
        self.parameters_clip.add().name = parameter_name
        return True

    def try_add_asset(self, parameter_name):
        if self.exists(parameter_name):
            return False
        self.parameters_asset.add().name = parameter_name
        return True

    def get(self, parameter_name):
        for collection in (self.parameters_float, self.parameters_bool, self.parameters_clip, self.parameters_asset):
            param = collection.get(parameter_name, None)
            if param is not None:
                return param.value

        return None

    def get_float(self, parameter_name):
        param = self.parameters_float.get(parameter_name, None)
        return param.value if param is not None else None

    def get_bool(self, parameter_name):
        param = self.parameters_bool.get(parameter_name, None)
        return param.value if param is not None else None

    def get_clip(self, parameter_name):
        param = self.parameters_clip.get(parameter_name, None)
        return param.value if param is not None else None

    def get_asset(self, parameter_name):
        param = self.parameters_asset.get(parameter_name, None)
        return param.value if param is not None else None

    def set(self, parameter_name, value):
        for collection in (self.parameters_float, self.parameters_bool, self.parameters_clip, self.parameters_asset):
            param = collection.get(parameter_name, None)
            if param is not None:
                param.value = value
                return

    def set_float(self, parameter_name, value):
        param = self.parameters_float.get(parameter_name, None)
        if param is not None:
            param.value = value

    def set_bool(self, parameter_name, value):
        param = self.parameters_bool.get(parameter_name, None)
        if param is not None:
            param.value = value

    def set_clip(self, parameter_name, value):
        param = self.parameters_clip.get(parameter_name, None)
        if param is not None:
            param.value = value

    def set_asset(self, parameter_name, value):
        param = self.parameters_asset.get(parameter_name, None)
        if param is not None:
            param.value = value


ATNodeParameterIds = {
    "StateMachine": [
    ],
    "Tail": [
    ],
    "InlinedStateMachine": [
    ],
    "Blend": [
        ("BLEND_FILTER", "Filter", "Filter", 0),  # rage::crFrameFilter
        ("BLEND_WEIGHT", "Weight", "Weight", 1),  # float
    ],
    "AddSubtract": [
        ("ADDSUBTRACT_FILTER", "Filter", "Filter", 0),  # rage::crFrameFilter
        ("ADDSUBTRACT_WEIGHT", "Weight", "Weight", 1),  # float
    ],
    "Filter": [
        ("FILTER_FILTER", "Filter", "Filter", 0),  # rage::crFrameFilter
    ],
    "Mirror": [
        ("MIRROR_FILTER", "Filter", "Filter", 0),  # rage::crFrameFilter
    ],
    "Frame": [
        ("FRAME_FRAME", "Frame", "Frame", 0),  # rage::crFrame
    ],
    "Ik": [
    ],
    "BlendN": [
        None,
        ("BLENDN_FILTER", "Filter", "Filter", 1),  # rage::crFrameFilter
        ("BLENDN_CHILDWEIGHT", "Child Weight", "Child Weight", 2),  # float (extra arg is the child index)
        ("BLENDN_CHILDFILTER", "Child Filter", "Child Filter", 3),  # rage::crFrameFilter (extra arg is the child index)
    ],
    "Clip": [
        ("CLIP_CLIP", "Clip", "Clip", 0),  # rage::crClip
        ("CLIP_PHASE", "Phase", "Phase", 1),  # float
        ("CLIP_RATE", "Rate", "Rate", 2),  # float
        ("CLIP_DELTA", "Delta", "Delta", 3),  # float
        ("CLIP_LOOPED", "Looped", "Looped", 4),  # bool
    ],
    "Extrapolate": [
        ("EXTRAPOLATE_DAMPING", "Damping", "Damping", 0),  # float
    ],
    "Expression": [
        ("EXPRESSION_EXPRESSION", "Expression", "Expression", 0),  # rage::crExpressions
        ("EXPRESSION_WEIGHT", "Weight", "Weight", 1),  # float
        ("EXPRESSION_VARIABLE", "Variable", "Variable", 2),  # float (extra arg is the variable name hash)
    ],
    "Capture": [
        ("CAPTURE_FRAME", "Frame", "Frame", 0),  # rage::crFrame
    ],
    "Proxy": [
        ("PROXY_NODE", "Node", "Node", 0),  # rage::crmtNode
    ],
    "AddN": [
        None,
        ("ADDN_FILTER", "Filter", "Filter", 1),  # rage::crFrameFilter
        ("ADDN_CHILDWEIGHT", "Child Weight", "Child Weight", 2),  # float (extra arg is the child index)
        ("ADDN_CHILDFILTER", "Child Filter", "Child Filter", 3),  # rage::crFrameFilter (extra arg is the child index)
    ],
    "Identity": [
    ],
    "Merge": [
        ("MERGE_FILTER", "Filter", "Filter", 0),  # rage::crFrameFilter
    ],
    "Pose": [
        ("POSE_ISNORMALIZED", "Is Normalized", "Is Normalized", 0),  # bool (getter hardcoded to true, setter does nothing)
    ],
    "MergeN": [
        None,
        ("MERGEN_FILTER", "Filter", "Filter", 1),  # rage::crFrameFilter
        ("MERGEN_CHILDWEIGHT", "Child Weight", "Child Weight", 2),  # float (extra arg is the child index)
        ("MERGEN_CHILDFILTER", "Child Filter", "Child Filter", 3),  # rage::crFrameFilter (extra arg is the child index)
    ],
    "Invalid": [
    ],
    "JointLimit": [
        ("JOINTLIMIT_FILTER", "Filter", "Filter", 0),  # rage::crFrameFilter (only setter exists)
    ],
}


def get_node_parameter_ids_by_type(node_type):
    return ATNodeParameterIds.get(node_type, [])


ATNodeParameterDataTypes = {
    "BLEND_FILTER": "asset",
    "BLEND_WEIGHT": "float",
    "ADDSUBTRACT_FILTER": "asset",
    "ADDSUBTRACT_WEIGHT": "float",
    "FILTER_FILTER": "asset",
    "MIRROR_FILTER": "asset",
    "FRAME_FRAME": "asset",  # TODO: how should we handle rage::crFrame parameters?
    "BLENDN_FILTER": "asset",
    "BLENDN_CHILDWEIGHT": "float",
    "BLENDN_CHILDFILTER": "asset",
    "CLIP_CLIP": "clip",
    "CLIP_PHASE": "float",
    "CLIP_RATE": "float",
    "CLIP_DELTA": "float",
    "CLIP_LOOPED": "bool",
    "EXTRAPOLATE_DAMPING": "float",
    "EXPRESSION_EXPRESSION": "asset",
    "EXPRESSION_WEIGHT": "float",
    "EXPRESSION_VARIABLE": "float",
    "CAPTURE_FRAME": "asset",  # TODO: how should we handle rage::crFrame parameters?
    "PROXY_NODE": "asset",  # TODO: how should we handle rage::crmtNode parameters?
    "ADDN_FILTER": "asset",
    "ADDN_CHILDWEIGHT": "float",
    "ADDN_CHILDFILTER": "asset",
    "MERGE_FILTER": "asset",
    "POSE_ISNORMALIZED": "bool",
    "MERGEN_FILTER": "asset",
    "MERGEN_CHILDWEIGHT": "float",
    "MERGEN_CHILDFILTER": "asset",
    "JOINTLIMIT_FILTER": "asset",
}


ATNodeEventIds = {
    "Clip": [
        ("CLIP_ITERATIONFINISHED", "Iteration Finished", "Triggered when a looped clip iteration finishes playing", 0),
        ("CLIP_FINISHED", "Finished", "Triggered when a non-looped clip finishes playing", 1),
        ("CLIP_UNK2", "Unk2", "Unk2", 2),
        ("CLIP_UNK3", "Unk3", "Unk3", 3),
        ("CLIP_UNK4", "Unk4", "Unk4", 4),
    ]
}


def get_node_event_ids_by_type(node_type):
    return ATNodeEventIds.get(node_type, [])


class ATNodeInputParameter(bpy.types.PropertyGroup):
    def get_available_node_parameter_ids(self, context):
        return get_node_parameter_ids_by_type(self.target_node_type)

    source_parameter_name: bpy.props.StringProperty(name="Source Parameter", default="")
    target_node_parameter_id: bpy.props.EnumProperty(name="Target Node Parameter ID", items=get_available_node_parameter_ids)
    target_node_parameter_extra_arg: bpy.props.IntProperty(name="Target Node Parameter Extra Arg", default=0)
    target_node_type: bpy.props.StringProperty(default="")  # only required for get_node_parameter_ids

    def set_target_node_parameter_id(self, parameter_id_int):
        assert self.target_node_type != "", "target_node_type must be set before calling set_target_node_parameter_id"
        self.target_node_parameter_id = self.get_available_node_parameter_ids(None)[parameter_id_int][0]

    def get_parameter_data_type(self):
        return ATNodeParameterDataTypes[self.target_node_parameter_id]


class ATNodeOutputParameter(bpy.types.PropertyGroup):
    def get_available_node_parameter_ids(self, context):
        return get_node_parameter_ids_by_type(self.source_node_type)

    target_parameter_name: bpy.props.StringProperty(name="Target Parameter", default="")
    source_node_parameter_id: bpy.props.EnumProperty(name="Source Node Parameter ID", items=get_available_node_parameter_ids)
    source_node_parameter_extra_arg: bpy.props.IntProperty(name="Source Node Parameter Extra Arg", default=0)
    source_node_type: bpy.props.StringProperty(default="")  # only required for get_node_parameter_ids

    def set_source_node_parameter_id(self, parameter_id_int):
        assert self.source_node_type != "", "source_node_type must be set before calling set_source_node_parameter_id"
        self.source_node_parameter_id = self.get_available_node_parameter_ids(None)[parameter_id_int][0]

    def get_parameter_data_type(self):
        return ATNodeParameterDataTypes[self.source_node_parameter_id]


class ATNodeEvent(bpy.types.PropertyGroup):
    def get_available_node_event_ids(self, context):
        return get_node_event_ids_by_type(self.node_type)

    node_event_id: bpy.props.EnumProperty(name="Node Event ID", items=get_available_node_event_ids)
    parameter_name: bpy.props.StringProperty(name="Parameter", default="")
    node_type: bpy.props.StringProperty(default="")  # only required for get_node_event_ids

    def set_node_event_id(self, event_id_int):
        assert self.node_type != "", "node_type must be set before calling set_node_event_id"
        self.node_event_id = self.get_available_node_event_ids(None)[event_id_int][0]


ATNodeOperatorTypes = [
    ("PushLiteral", "PushLiteral", "PushLiteral", 0),
    ("PushParameter", "PushParameter", "PushParameter", 1),
    ("Add", "Add", "Add", 2),
    ("Multiply", "Multiply", "Multiply", 3),
    ("Remap", "Remap", "Remap", 4),
]


def ATNodeOperatorTypeProperty(name=""):
    return bpy.props.EnumProperty(name=name, items=ATNodeOperatorTypes)


class ATNodeOperatorRemapRange(bpy.types.PropertyGroup):
    percent: bpy.props.FloatProperty(name="Percent", default=0.0, min=0.0, max=1.0)
    min: bpy.props.FloatProperty(name="Min", default=0.0)
    length: bpy.props.FloatProperty(name="Length", default=0.0)


class ATNodeOperator(bpy.types.PropertyGroup):
    type: ATNodeOperatorTypeProperty(name="Type")
    parameter_name: bpy.props.StringProperty(name="Parameter", default="")
    value: bpy.props.FloatProperty(name="Value", default=0.0)
    min: bpy.props.FloatProperty(name="Min", default=0.0)
    max: bpy.props.FloatProperty(name="Max", default=0.0)
    remap_ranges: bpy.props.CollectionProperty(name="Ranges", type=ATNodeOperatorRemapRange)

    def set(self, op: MoveStateOperatorBase):
        self.type = op.type
        if self.type == "PushLiteral":
            self.value = op.value
        elif self.type == "PushParameter":
            self.parameter_name = op.parameter_name
        elif self.type == "Add" or self.type == "Multiply":
            pass  # nothing to do
        elif self.type == "Remap":
            self.min = op.min
            self.max = op.max
            self.remap_ranges.clear()
            for r in op.ranges:
                remap_range = self.remap_ranges.add()
                remap_range.percent = r.percent
                remap_range.min = r.min
                remap_range.length = r.length

    def draw(self, context, layout, draw_parameter_name_prop=None):
        row = layout.row()
        row.prop(self, "type", text="")
        if self.type == "PushLiteral":
            row.prop(self, "value", text="")
        elif self.type == "PushParameter":
            if draw_parameter_name_prop is not None:
                draw_parameter_name_prop(row, self, "parameter_name", "float", text="")
            else:
                row.prop(self, "parameter_name", text="")
        elif self.type == "Remap":
            row.prop(self, "min", text="")
            row.prop(self, "max", text="")
            for r in self.remap_ranges:
                range_row = layout.row()
                range_row.separator(factor=1.0)
                range_row.prop(r, "percent")
                range_row.prop(r, "min")
                range_row.prop(r, "length")


class ATNodeOperation(bpy.types.PropertyGroup):
    def get_available_node_parameter_ids(self, context):
        return list(filter(lambda e: e is not None and ATNodeParameterDataTypes[e[0]] == "float",
                           get_node_parameter_ids_by_type(self.node_type)))

    node_parameter_id: bpy.props.EnumProperty(name="Node Parameter ID", items=get_available_node_parameter_ids)
    node_parameter_extra_arg: bpy.props.IntProperty(name="Node Parameter Extra Arg", default=0)
    operators: bpy.props.CollectionProperty(name="Operators", type=ATNodeOperator)
    node_type: bpy.props.StringProperty(default="")  # only required for get_node_parameter_ids

    def set_node_parameter_id(self, parameter_id_int):
        assert self.node_type != "", "node_type must be set before calling set_node_parameter_id"
        self.node_parameter_id = get_node_parameter_ids_by_type(self.node_type)[parameter_id_int][0]
