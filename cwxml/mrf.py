from abc import ABC as AbstractClass
from xml.etree import ElementTree as ET

from numpy import float32

from .element import (
    AttributeProperty,
    Element,
    ElementTree,
    ElementProperty,
    ListPropertyRequired,
    TextProperty,
    TextPropertyRequired,
    ValueProperty,
    get_str_type
)


class MRF:
    file_extension = ".mrf.xml"

    @staticmethod
    def from_xml_file(filepath):
        return MoveNetwork.from_xml_file(filepath)

    @staticmethod
    def write_xml(move_network, filepath):
        return move_network.write_xml(filepath)


class MoveNetworkBit(ElementTree, AbstractClass):

    def __init__(self):
        super().__init__()
        self.name = TextPropertyRequired("Name", "")
        self.bit_position = ValueProperty("BitPosition", 0)


class MoveNetworkTrigger(MoveNetworkBit):
    tag_name = "Item"


class MoveNetworkFlag(MoveNetworkBit):
    tag_name = "Item"


class MoveNetworkTriggersList(ListPropertyRequired):
    list_type = MoveNetworkTrigger
    tag_name = "MoveNetworkTriggers"


class MoveNetworkFlagsList(ListPropertyRequired):
    list_type = MoveNetworkFlag
    tag_name = "MoveNetworkFlags"


class MoveParameterizedValueProperty(Element):
    tag_name = None

    def __init__(self, tag_name, value=None, parameter=None):
        super().__init__()
        self.tag_name = tag_name
        self.value = value
        self.parameter = parameter

    @staticmethod
    def from_xml(element: ET.Element):
        if "value" in element.attrib:
            return MoveParameterizedValueProperty(element.tag, value=get_str_type(element.get("value")))
        elif "parameter" in element.attrib:
            return MoveParameterizedValueProperty(element.tag, parameter=element.get("parameter"))

        return MoveParameterizedValueProperty(element.tag)

    def to_xml(self):
        if self.value is not None:
            value = self.value
            if type(value) is int:
                value = int(self.value)
            elif type(self.value) is float:
                value = int(self.value) if self.value.is_integer() else float32(self.value)
            attrib = {"value": str(value)}
        elif self.parameter:
            attrib = {"parameter": str(self.parameter)}
        else:
            attrib = {}
        return ET.Element(self.tag_name, attrib=attrib)


class MoveParameterizedClipProperty(Element):
    tag_name = None

    def __init__(self, tag_name, container_type=None, container_name=None, name=None, parameter=None):
        super().__init__()
        self.tag_name = tag_name
        self.container_type = container_type
        self.container_name = container_name
        self.name = name
        self.parameter = parameter

    @staticmethod
    def from_xml(element: ET.Element):
        container_type_elem = element.find("ContainerType")
        container_name_elem = element.find("ContainerName")
        name_elem = element.find("Name")
        if container_type_elem is not None and container_name_elem is not None and name_elem is not None:
            return MoveParameterizedClipProperty(element.tag,
                                                 container_type=container_type_elem.text,
                                                 container_name=container_name_elem.text,
                                                 name=name_elem.text)
        elif "parameter" in element.attrib:
            return MoveParameterizedClipProperty(element.tag, parameter=element.get("parameter"))

        return MoveParameterizedClipProperty(element.tag)

    def to_xml(self):
        children = None
        attrib = {}
        if self.container_type and self.container_name and self.name:
            container_type_elem = ET.Element("ContainerType")
            container_name_elem = ET.Element("ContainerName")
            name_elem = ET.Element("Name")
            container_type_elem.text = self.container_type
            container_name_elem.text = self.container_name
            name_elem.text = self.name
            children = [container_type_elem, container_name_elem, name_elem]
        elif self.parameter:
            attrib = {"parameter": str(self.parameter)}

        elem = ET.Element(self.tag_name, attrib=attrib)
        if children:
            elem.extend(children)
        return elem


class MoveParameterizedAssetProperty(Element):
    tag_name = None

    def __init__(self, tag_name, dictionary_name=None, name=None, parameter=None):
        super().__init__()
        self.tag_name = tag_name
        self.dictionary_name = dictionary_name
        self.name = name
        self.parameter = parameter

    @staticmethod
    def from_xml(element: ET.Element):
        dictionary_name_elem = element.find("DictionaryName")
        name_elem = element.find("Name")
        if dictionary_name_elem is not None and name_elem is not None:
            return MoveParameterizedAssetProperty(element.tag,
                                                  dictionary_name=dictionary_name_elem.text,
                                                  name=name_elem.text)
        elif "parameter" in element.attrib:
            return MoveParameterizedAssetProperty(element.tag, parameter=element.get("parameter"))

        return MoveParameterizedAssetProperty(element.tag)

    def to_xml(self):
        children = None
        attrib = {}
        if self.dictionary_name and self.name:
            dictionary_name_elem = ET.Element("DictionaryName")
            name_elem = ET.Element("Name")
            dictionary_name_elem.text = self.dictionary_name
            name_elem.text = self.name
            children = [dictionary_name_elem, name_elem]
        elif self.parameter:
            attrib = {"parameter": str(self.parameter)}

        elem = ET.Element(self.tag_name, attrib=attrib)
        if children:
            elem.extend(children)
        return elem


class MoveNodeRef(ElementProperty):
    value_types = (str)

    def __init__(self, tag_name: str, value=None):
        super().__init__(tag_name, value)

    @staticmethod
    def from_xml(element: ET.Element):
        if not "ref" in element.attrib:
            MoveNodeRef.read_value_error(element)

        return MoveNodeRef(element.tag, element.get("ref"))

    def to_xml(self):
        value = self.value
        return ET.Element(self.tag_name, attrib={"ref": str(value)})


# NODES BASE CLASSES

class MoveNodeBase(ElementTree, AbstractClass):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.type = AttributeProperty("type", self.type)
        self.name = TextPropertyRequired("Name", "")
        self.node_index = ValueProperty("NodeIndex", 0)


class MoveNodeStateBase(MoveNodeBase):
    def __init__(self):
        super().__init__()
        self.state_unk3 = ValueProperty("StateUnk3", 0)
        self.entry_parameter_name = TextPropertyRequired("EntryParameterName")
        self.exit_parameter_name = TextPropertyRequired("ExitParameterName")


class MoveNodePairBase(MoveNodeBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.child0 = MoveAnyNode("Child0")
        self.child1 = MoveAnyNode("Child1")


class MoveNodePairWeightedBase(MoveNodePairBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.child0_influence_override = TextPropertyRequired("Child0InfluenceOverride")
        self.child1_influence_override = TextPropertyRequired("Child1InfluenceOverride")
        self.weight = MoveParameterizedValueProperty("Weight")
        self.frame_filter = MoveParameterizedAssetProperty("FrameFilter")
        self.synchronizer_type = TextPropertyRequired("SynchronizerType")
        self.synchronizer_tag_flags = TextProperty("SynchronizerTagFlags")
        self.merge_blend = ValueProperty("MergeBlend", False)
        self.unk_flag6 = ValueProperty("UnkFlag6", False)
        self.unk_flag7 = ValueProperty("UnkFlag7", 0)
        self.unk_flag21 = ValueProperty("UnkFlag21", 0)
        self.unk_flag23 = ValueProperty("UnkFlag23", 0)
        self.unk_flag25 = ValueProperty("UnkFlag25", 0)


class MoveNodeWithChildBase(MoveNodeBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.child = MoveAnyNode("Child")


class MoveNodeWithChildAndFilterBase(MoveNodeWithChildBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.frame_filter = MoveParameterizedAssetProperty("FrameFilter")


class MoveNodeNChildren(ListPropertyRequired):
    class Child(ElementTree):
        tag_name = "Item"

        def __init__(self):
            super().__init__()
            self.weight = MoveParameterizedValueProperty("Weight")
            self.frame_filter = MoveParameterizedAssetProperty("FrameFilter")
            self.node = MoveAnyNode("Node")

    list_type = Child
    tag_name = "Children"


class MoveNodeNBase(MoveNodeBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.frame_filter = MoveParameterizedAssetProperty("FrameFilter")
        self.synchronizer_type = TextPropertyRequired("SynchronizerType")
        self.synchronizer_tag_flags = TextProperty("SynchronizerTagFlags")
        self.zero_destination = ValueProperty("ZeroDestination", False)
        self.children = MoveNodeNChildren()


class MoveStatesList(ListPropertyRequired):
    list_type = MoveNodeStateBase
    tag_name = "States"

    @staticmethod
    def from_xml(element: ET.Element):
        new = MoveStatesList()

        for child in element.findall("Item"):
            if "type" in child.attrib:
                state_type = child.get("type")
                if state_type == MoveNodeState.type:
                    new.value.append(MoveNodeState.from_xml(child))
                elif state_type == MoveNodeStateMachine.type:
                    new.value.append(MoveNodeStateMachine.from_xml(child))

        return new


class MoveConditionBase(ElementTree, AbstractClass):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.type = AttributeProperty("type", self.type)


class MoveConditionWithParameterAndRangeBase(MoveConditionBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.parameter = TextPropertyRequired("ParameterName")
        self.min = ValueProperty("Min", 0.0)
        self.max = ValueProperty("Max", 0.0)


class MoveConditionWithParameterAndValueBase(MoveConditionBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.parameter = TextPropertyRequired("ParameterName")
        self.value = ValueProperty("Value")  # float or bool


class MoveConditionWithValueBase(MoveConditionBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.value = ValueProperty("Value", 0.0)


class MoveConditionBitTestBase(MoveConditionBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.bit_position = ValueProperty("BitPosition", 0)
        self.invert = ValueProperty("Invert", False)


class MoveConditionParameterInsideRange(MoveConditionWithParameterAndRangeBase):
    type = "ParameterInsideRange"


class MoveConditionParameterOutsideRange(MoveConditionWithParameterAndRangeBase):
    type = "ParameterOutsideRange"


class MoveConditionMoveNetworkTrigger(MoveConditionBitTestBase):
    type = "MoveNetworkTrigger"


class MoveConditionMoveNetworkFlag(MoveConditionBitTestBase):
    type = "MoveNetworkFlag"


class MoveConditionParameterGreaterThan(MoveConditionWithParameterAndValueBase):
    type = "ParameterGreaterThan"


class MoveConditionParameterGreaterOrEqual(MoveConditionWithParameterAndValueBase):
    type = "ParameterGreaterOrEqual"


class MoveConditionParameterLessThan(MoveConditionWithParameterAndValueBase):
    type = "ParameterLessThan"


class MoveConditionParameterLessOrEqual(MoveConditionWithParameterAndValueBase):
    type = "ParameterLessOrEqual"


class MoveConditionTimeGreaterThan(MoveConditionWithValueBase):
    type = "TimeGreaterThan"


class MoveConditionTimeLessThan(MoveConditionWithValueBase):
    type = "TimeLessThan"


class MoveConditionEventOccurred(MoveConditionWithParameterAndValueBase):
    type = "EventOccurred"


class MoveConditionBoolParameterExists(MoveConditionWithParameterAndValueBase):
    type = "BoolParameterExists"


class MoveConditionBoolParameterEquals(MoveConditionWithParameterAndValueBase):
    type = "BoolParameterEquals"


class MoveConditionsList(ListPropertyRequired):
    list_type = MoveConditionBase
    tag_name = "Conditions"

    @staticmethod
    def from_xml(element: ET.Element):
        new = MoveConditionsList()

        for child in element.findall("Item"):
            if "type" in child.attrib:
                cond_type = child.get("type")
                if cond_type == MoveConditionParameterInsideRange.type:
                    new.value.append(MoveConditionParameterInsideRange.from_xml(child))
                elif cond_type == MoveConditionParameterOutsideRange.type:
                    new.value.append(MoveConditionParameterOutsideRange.from_xml(child))
                elif cond_type == MoveConditionMoveNetworkTrigger.type:
                    new.value.append(MoveConditionMoveNetworkTrigger.from_xml(child))
                elif cond_type == MoveConditionMoveNetworkFlag.type:
                    new.value.append(MoveConditionMoveNetworkFlag.from_xml(child))
                elif cond_type == MoveConditionParameterGreaterThan.type:
                    new.value.append(MoveConditionParameterGreaterThan.from_xml(child))
                elif cond_type == MoveConditionParameterGreaterOrEqual.type:
                    new.value.append(MoveConditionParameterGreaterOrEqual.from_xml(child))
                elif cond_type == MoveConditionParameterLessThan.type:
                    new.value.append(MoveConditionParameterLessThan.from_xml(child))
                elif cond_type == MoveConditionParameterLessOrEqual.type:
                    new.value.append(MoveConditionParameterLessOrEqual.from_xml(child))
                elif cond_type == MoveConditionTimeGreaterThan.type:
                    new.value.append(MoveConditionTimeGreaterThan.from_xml(child))
                elif cond_type == MoveConditionTimeLessThan.type:
                    new.value.append(MoveConditionTimeLessThan.from_xml(child))
                elif cond_type == MoveConditionEventOccurred.type:
                    new.value.append(MoveConditionEventOccurred.from_xml(child))
                elif cond_type == MoveConditionBoolParameterExists.type:
                    new.value.append(MoveConditionBoolParameterExists.from_xml(child))
                elif cond_type == MoveConditionBoolParameterEquals.type:
                    new.value.append(MoveConditionBoolParameterEquals.from_xml(child))

        return new


class MoveStateTransition(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.target_state = MoveNodeRef("TargetState")
        self.duration = ValueProperty("Duration", 0.0)
        self.duration_parameter_name = TextPropertyRequired("DurationParameterName")
        self.progress_parameter_name = TextPropertyRequired("ProgressParameterName")
        self.blend_modifier = TextPropertyRequired("BlendModifier")
        self.synchronizer_type = TextPropertyRequired("SynchronizerType")
        self.synchronizer_tag_flags = TextProperty("SynchronizerTagFlags")
        self.frame_filter = MoveParameterizedAssetProperty("FrameFilter")  # note: cannot actually use parameters here
        self.unk_flag2_detach_update_observers = ValueProperty("UnkFlag2_DetachUpdateObservers", False)
        self.unk_flag18 = ValueProperty("UnkFlag18", False)
        self.unk_flag19 = ValueProperty("UnkFlag19", False)
        self.conditions = MoveConditionsList()


class MoveStateTransitionsList(ListPropertyRequired):
    list_type = MoveStateTransition
    tag_name = "Transitions"


class MoveStateInputParameter(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.source_parameter_name = TextPropertyRequired("SourceParameterName")
        self.target_node_index = ValueProperty("TargetNodeIndex", 0)
        self.target_node_parameter_id = ValueProperty("TargetNodeParameterId", 0)
        self.target_node_parameter_extra_arg = ValueProperty("TargetNodeParameterExtraArg", 0)


class MoveStateInputParametersList(ListPropertyRequired):
    list_type = MoveStateInputParameter
    tag_name = "InputParameters"


class MoveStateOutputParameter(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.target_parameter_name = TextPropertyRequired("TargetParameterName")
        self.source_node_index = ValueProperty("SourceNodeIndex", 0)
        self.source_node_parameter_id = ValueProperty("SourceNodeParameterId", 0)
        self.source_node_parameter_extra_arg = ValueProperty("SourceNodeParameterExtraArg", 0)


class MoveStateOutputParametersList(ListPropertyRequired):
    list_type = MoveStateOutputParameter
    tag_name = "OutputParameters"


class MoveStateEvent(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.node_index = ValueProperty("NodeIndex", 0)
        self.node_event_id = ValueProperty("NodeEventId", 0)
        self.parameter_name = TextPropertyRequired("ParameterName")


class MoveStateEventsList(ListPropertyRequired):
    list_type = MoveStateEvent
    tag_name = "Events"


class MoveStateOperatorBase(ElementTree, AbstractClass):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.type = AttributeProperty("type", self.type)


class MoveStateOperatorFinish(MoveStateOperatorBase):
    type = "Finish"


class MoveStateOperatorPushLiteral(MoveStateOperatorBase):
    type = "PushLiteral"

    def __init__(self):
        super().__init__()
        self.value = ValueProperty("Value", 0.0)


class MoveStateOperatorPushParameter(MoveStateOperatorBase):
    type = "PushParameter"

    def __init__(self):
        super().__init__()
        self.parameter_name = TextPropertyRequired("ParameterName")


class MoveStateOperatorAdd(MoveStateOperatorBase):
    type = "Add"


class MoveStateOperatorMultiply(MoveStateOperatorBase):
    type = "Multiply"


class MoveStateOperatorRemapRanges(ListPropertyRequired):
    class Range(ElementTree):
        tag_name = "Item"

        def __init__(self):
            super().__init__()
            self.percent = ValueProperty("Percent", 0.0)
            self.min = ValueProperty("Min", 0.0)
            self.length = ValueProperty("Length", 0.0)

    list_type = Range
    tag_name = "Ranges"


class MoveStateOperatorRemap(MoveStateOperatorBase):
    type = "Remap"

    def __init__(self):
        super().__init__()
        self.min = ValueProperty("Min", 0.0)
        self.max = ValueProperty("Max", 0.0)
        self.ranges = MoveStateOperatorRemapRanges()


class MoveStateOperatorsList(ListPropertyRequired):
    list_type = MoveStateOperatorBase
    tag_name = "Operators"

    @staticmethod
    def from_xml(element: ET.Element):
        new = MoveStateOperatorsList()

        for child in element.findall("Item"):
            if "type" in child.attrib:
                cond_type = child.get("type")
                if cond_type == MoveStateOperatorFinish.type:
                    new.value.append(MoveStateOperatorFinish.from_xml(child))
                elif cond_type == MoveStateOperatorPushLiteral.type:
                    new.value.append(MoveStateOperatorPushLiteral.from_xml(child))
                elif cond_type == MoveStateOperatorPushParameter.type:
                    new.value.append(MoveStateOperatorPushParameter.from_xml(child))
                elif cond_type == MoveStateOperatorAdd.type:
                    new.value.append(MoveStateOperatorAdd.from_xml(child))
                elif cond_type == MoveStateOperatorMultiply.type:
                    new.value.append(MoveStateOperatorMultiply.from_xml(child))
                elif cond_type == MoveStateOperatorRemap.type:
                    new.value.append(MoveStateOperatorRemap.from_xml(child))

        return new


class MoveStateOperation(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.node_index = ValueProperty("NodeIndex", 0)
        self.node_parameter_id = ValueProperty("NodeParameterId", 0)
        self.node_parameter_extra_arg = ValueProperty("NodeParameterExtraArg", 0)
        self.operators = MoveStateOperatorsList()


class MoveStateOperationsList(ListPropertyRequired):
    list_type = MoveStateOperation
    tag_name = "Operations"


# NODE IMPLEMENTATIONS

class MoveNodeStateMachine(MoveNodeStateBase):
    type = "StateMachine"

    def __init__(self):
        super().__init__()
        self.initial_state = MoveNodeRef("InitialState")
        self.states = MoveStatesList()
        self.transitions = MoveStateTransitionsList()


class MoveNodeTail(MoveNodeBase):
    type = "Tail"


class MoveNodeInlinedStateMachine(MoveNodeStateBase):
    type = "InlinedStateMachine"

    def __init__(self):
        super().__init__()
        self.initial_state = MoveNodeRef("InitialState")
        self.states = MoveStatesList()
        self.fallback_node = MoveAnyNode("FallbackNode")


class MoveNodeBlend(MoveNodePairWeightedBase):
    type = "Blend"


class MoveNodeAddSubtract(MoveNodePairWeightedBase):
    type = "AddSubtract"


class MoveNodeFilter(MoveNodeWithChildAndFilterBase):
    type = "Filter"


class MoveNodeMirror(MoveNodeWithChildAndFilterBase):
    type = "Mirror"


class MoveNodeFrame(MoveNodeBase):
    type = "Frame"

    def __init__(self):
        super().__init__()
        self.frame = MoveParameterizedAssetProperty("Frame")  # note, only parameters supported


class MoveNodeIk(MoveNodeBase):
    type = "Ik"


class MoveNodeBlendN(MoveNodeNBase):
    type = "BlendN"


class MoveNodeClip(MoveNodeBase):
    type = "Clip"

    def __init__(self):
        super().__init__()
        self.clip = MoveParameterizedClipProperty("Clip")
        self.phase = MoveParameterizedValueProperty("Phase")
        self.rate = MoveParameterizedValueProperty("Rate")
        self.delta = MoveParameterizedValueProperty("Delta")
        self.looped = MoveParameterizedValueProperty("Looped")
        self.unk_flag10 = ValueProperty("UnkFlag10", 0)


class MoveNodeExtrapolate(MoveNodeWithChildBase):
    type = "Extrapolate"

    def __init__(self):
        super().__init__()
        self.damping = MoveParameterizedValueProperty("Damping")


class MoveExpressionVariablesList(ListPropertyRequired):
    class Variable(ElementTree):
        tag_name = "Item"

        def __init__(self):
            super().__init__()
            self.name = TextPropertyRequired("Name")
            self.value = MoveParameterizedValueProperty("Value")

    list_type = Variable
    tag_name = "Variables"


class MoveNodeExpression(MoveNodeWithChildBase):
    type = "Expression"

    def __init__(self):
        super().__init__()
        self.weight = MoveParameterizedValueProperty("Weight")
        self.expression = MoveParameterizedAssetProperty("Expression")
        self.variables = MoveExpressionVariablesList()


class MoveNodeCapture(MoveNodeWithChildBase):
    type = "Capture"

    def __init__(self):
        super().__init__()
        self.frame = MoveParameterizedAssetProperty("Frame")  # note, only parameters supported


class MoveNodeProxy(MoveNodeBase):
    type = "Proxy"

    def __init__(self):
        super().__init__()
        self.node_parameter_name = TextPropertyRequired("NodeParameterName")


class MoveNodeAddN(MoveNodeNBase):
    type = "AddN"


class MoveNodeIdentity(MoveNodeBase):
    type = "Identity"


class MoveNodeMerge(MoveNodePairBase):
    type = "Merge"

    def __init__(self):
        super().__init__()
        self.child0_influence_override = TextPropertyRequired("Child0InfluenceOverride")
        self.child1_influence_override = TextPropertyRequired("Child1InfluenceOverride")
        self.frame_filter = MoveParameterizedAssetProperty("FrameFilter")
        self.synchronizer_type = TextPropertyRequired("SynchronizerType")
        self.synchronizer_tag_flags = TextProperty("SynchronizerTagFlags")
        self.unk_flag6 = ValueProperty("UnkFlag6", False)
        self.unk_flag7 = ValueProperty("UnkFlag7", 0)
        self.unk_flag21 = ValueProperty("UnkFlag21", 0)


class MoveNodePose(MoveNodeBase):
    type = "Pose"


class MoveNodeMergeN(MoveNodeNBase):
    type = "MergeN"


class MoveNodeState(MoveNodeStateBase):
    type = "State"

    def __init__(self):
        super().__init__()
        self.initial_node = MoveAnyNode("InitialNode")
        self.transitions = MoveStateTransitionsList()
        self.input_parameters = MoveStateInputParametersList()
        self.output_parameters = MoveStateOutputParametersList()
        self.events = MoveStateEventsList()
        self.operations = MoveStateOperationsList()


class MoveNodeInvalid(MoveNodeBase):
    type = "Invalid"


class MoveNodeJointLimit(MoveNodeWithChildAndFilterBase):
    type = "JointLimit"


class MoveNodeSubNetwork(MoveNodeBase):
    type = "SubNetwork"

    def __init__(self):
        super().__init__()
        self.subnetwork_parameter_name = TextPropertyRequired("SubNetworkParameterName")


MoveNodeTypes = [
    MoveNodeStateMachine,
    MoveNodeTail,
    MoveNodeInlinedStateMachine,
    MoveNodeBlend,
    MoveNodeAddSubtract,
    MoveNodeFilter,
    MoveNodeMirror,
    MoveNodeFrame,
    MoveNodeIk,
    MoveNodeBlendN,
    MoveNodeClip,
    MoveNodeExtrapolate,
    MoveNodeExpression,
    MoveNodeCapture,
    MoveNodeProxy,
    MoveNodeAddN,
    MoveNodeIdentity,
    MoveNodeMerge,
    MoveNodePose,
    MoveNodeMergeN,
    MoveNodeState,
    MoveNodeInvalid,
    MoveNodeJointLimit,
    MoveNodeSubNetwork
]

MoveNodeTypesDictionary = {Node.type: Node for Node in MoveNodeTypes}


class MoveAnyNode(ElementTree):
    tag_name = None

    def __init__(self, tag_name):
        super().__init__()
        self.tag_name = tag_name

    @staticmethod
    def from_xml(element: ET.Element):
        node = None
        if "type" in element.attrib:
            node_type = element.get("type")
            if node_type in MoveNodeTypesDictionary:
                node = MoveNodeTypesDictionary[node_type].from_xml(element)
            else:
                raise TypeError("Invalid node type '%s'" % node_type)

        if node:
            node.tag_name = element.tag
            return node
        else:
            MoveAnyNode.read_value_error(element)


class MoveNetworkUnk1(ElementTree):
    tag_name = "Unk1"


class MoveNetworkUnkBytes(ElementTree):
    tag_name = "UnkBytes"


class MoveNetwork(ElementTree, AbstractClass):
    tag_name = "MoveNetwork"

    def __init__(self):
        super().__init__()
        self.triggers = MoveNetworkTriggersList()
        self.flags = MoveNetworkFlagsList()
        self.root_state = None
        self.unk1 = MoveNetworkUnk1()
        self.unk_bytes = MoveNetworkUnkBytes()

    @classmethod
    def from_xml(cls, element: ET.Element):
        new = super().from_xml(element)
        root_state_elem = element.find("RootState")
        root_state_type = root_state_elem.get("type")
        root_state = None
        if root_state_type == MoveNodeState.type:
            root_state = MoveNodeState.from_xml(root_state_elem)
        elif root_state_type == MoveNodeStateMachine.type:
            root_state = MoveNodeStateMachine.from_xml(root_state_elem)
        else:
            raise TypeError("Invalid root state node type")

        if root_state:
            root_state.tag_name = "RootState"
            new.root_state = root_state
        return new
