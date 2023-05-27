from abc import ABC as AbstractClass
from xml.etree import ElementTree as ET

from numpy import float32

from .element import (
    AttributeProperty,
    Element,
    ElementTree,
    ElementProperty,
    ListProperty,
    TextProperty,
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
        self.name = TextProperty("Name", "")
        self.bit_position = ValueProperty("BitPosition", 0)


class MoveNetworkTrigger(MoveNetworkBit):
    tag_name = "Item"


class MoveNetworkFlag(MoveNetworkBit):
    tag_name = "Item"


class MoveNetworkTriggersList(ListProperty):
    list_type = MoveNetworkTrigger
    tag_name = "MoveNetworkTriggers"


class MoveNetworkFlagsList(ListProperty):
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


class MoveNodeBase(ElementTree, AbstractClass):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.type = AttributeProperty("type", self.type)
        self.name = TextProperty("Name", "")
        self.node_index = ValueProperty("NodeIndex", 0)


class MoveNodeWithChildBase(MoveNodeBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.child = MoveNodeAny("Child")


class MoveNodePairBase(MoveNodeBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.child0 = MoveNodeAny("Child0")
        self.child1 = MoveNodeAny("Child1")


class MoveNodeNChildren(ListProperty):
    class Child(ElementTree):
        tag_name = "Item"

        def __init__(self):
            super().__init__()
            self.weight = MoveParameterizedValueProperty("Weight")
            # self.frame_filter =
            self.node = MoveNodeAny("Node")

    list_type = Child
    tag_name = "Children"


class MoveNodeNBase(MoveNodeBase, AbstractClass):
    def __init__(self):
        super().__init__()
        self.children = MoveNodeNChildren()


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


class MoveStateBase(MoveNodeBase):
    def __init__(self):
        super().__init__()
        self.state_unk3 = ValueProperty("StateUnk3", 0)
        self.entry_parameter_name = TextProperty("EntryParameterName")
        self.exit_parameter_name = TextProperty("ExitParameterName")


class MoveStatesList(ListProperty):
    list_type = MoveStateBase
    tag_name = "States"

    @staticmethod
    def from_xml(element: ET.Element):
        new = MoveStatesList()

        for child in element.findall("Item"):
            if "type" in child.attrib:
                state_type = child.get("type")
                if state_type == "State":
                    new.value.append(MoveState.from_xml(child))
                elif state_type == "StateMachine":
                    new.value.append(MoveStateMachine.from_xml(child))

        return new


class MoveStateTransition(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.target_state = MoveNodeRef("TargetState")
        self.duration = ValueProperty("Duration", 0.0)
        self.duration_parameter_name = TextProperty("EntryParameterName")
        self.progress_parameter_name = TextProperty("ExitParameterName")
        self.blend_modifier = TextProperty("BlendModifier")
        self.synchronizer_type = TextProperty("SynchronizerType")


class MoveStateTransitionsList(ListProperty):
    list_type = MoveStateTransition
    tag_name = "Transitions"


class MoveState(MoveStateBase):
    type = "State"

    def __init__(self):
        super().__init__()
        self.initial_node = MoveNodeAny("InitialNode")
        self.transitions = MoveStateTransitionsList()


class MoveStateMachine(MoveStateBase):
    type = "StateMachine"

    def __init__(self):
        super().__init__()
        self.initial_state = MoveNodeRef("InitialState")
        self.states = MoveStatesList()
        self.transitions = MoveStateTransitionsList()


class MoveInvalid(MoveNodeBase):
    type = "Invalid"


class MoveClip(MoveNodeBase):
    type = "Clip"

    def __init__(self):
        super().__init__()
        self.clip = MoveParameterizedClipProperty("Clip")
        self.phase = MoveParameterizedValueProperty("Phase")
        self.rate = MoveParameterizedValueProperty("Rate")
        self.delta = MoveParameterizedValueProperty("Delta")
        self.looped = MoveParameterizedValueProperty("Looped")
        self.unk_flag10 = ValueProperty("UnkFlag10", 0)


class MoveBlend(MoveNodePairBase):
    type = "Blend"

    def __init__(self):
        super().__init__()
        self.weight = MoveParameterizedValueProperty("Weight")


class MoveBlendN(MoveNodeNBase):
    type = "BlendN"

    def __init__(self):
        super().__init__()


class MoveAddSubtract(MoveNodePairBase):
    type = "AddSubtract"

    def __init__(self):
        super().__init__()


class MoveFilter(MoveNodeWithChildBase):
    type = "Filter"

    def __init__(self):
        super().__init__()


class MoveExpression(MoveNodeWithChildBase):
    type = "Expression"

    def __init__(self):
        super().__init__()


class MoveNodeAny(ElementTree):
    tag_name = None

    def __init__(self, tag_name):
        super().__init__()
        self.tag_name = tag_name

    @staticmethod
    def from_xml(element: ET.Element):
        node = None
        if "type" in element.attrib:
            node_type = element.get("type")
            if node_type == "Invalid":
                node = MoveInvalid.from_xml(element)
            elif node_type == "State":
                node = MoveState.from_xml(element)
            elif node_type == "StateMachine":
                node = MoveStateMachine.from_xml(element)
            elif node_type == "Clip":
                node = MoveClip.from_xml(element)
            elif node_type == "Blend":
                node = MoveBlend.from_xml(element)
            elif node_type == "BlendN":
                node = MoveBlendN.from_xml(element)
            elif node_type == "AddSubtract":
                node = MoveAddSubtract.from_xml(element)
            elif node_type == "Filter":
                node = MoveFilter.from_xml(element)
            elif node_type == "Expression":
                node = MoveExpression.from_xml(element)
            else:
                raise TypeError("Invalid node type '%s'" % node_type)

        if node:
            node.tag_name = element.tag
            return node
        else:
            MoveNodeAny.read_value_error(element)


class MoveNetwork(ElementTree, AbstractClass):
    tag_name = "MoveNetwork"

    def __init__(self):
        super().__init__()
        self.triggers = MoveNetworkTriggersList()
        self.flags = MoveNetworkFlagsList()
        self.root_state = None
        # self.unk1 = None
        # self.unk_bytes = None

    @classmethod
    def from_xml(cls, element: ET.Element):
        new = super().from_xml(element)
        root_state_elem = element.find("RootState")
        root_state_type = root_state_elem.get("type")
        root_state = None
        if root_state_type == "State":
            root_state = MoveState.from_xml(root_state_elem)
        elif root_state_type == "StateMachine":
            root_state = MoveStateMachine.from_xml(root_state_elem)
        else:
            raise TypeError("Invalid root state node type")

        if root_state:
            root_state.tag_name = "RootState"
            new.root_state = root_state
        return new
