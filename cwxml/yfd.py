from xml.etree import ElementTree as ET
from .element import (
    Element,
    ElementTree,
    ElementProperty,
    ListPropertyRequired,
    TextPropertyRequired,
    ValueProperty,
)
from collections.abc import MutableSequence


class YFD:

    file_extension = ".yfd.xml"

    @staticmethod
    def from_xml_file(filepath):
        return FrameFilterDictionary.from_xml_file(filepath)

    @staticmethod
    def write_xml(frame_filter_dictionary, filepath):
        return frame_filter_dictionary.write_xml(filepath)


class FrameFilterEntry(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.track = ValueProperty("Track")
        self.bone_id = ValueProperty("BoneId")
        self.weight_index = ValueProperty("WeightIndex")


class FrameFilterEntriesList(ListPropertyRequired):
    list_type = FrameFilterEntry
    tag_name = "Entries"


class FrameFilterWeights(ElementProperty):
    value_types = list

    def __init__(self):
        super().__init__(tag_name="Weights", value=[])

    @classmethod
    def from_xml(cls, element: ET.Element):
        new = cls()
        weights = element.text.strip().replace("\n", "").split()
        new.value = [float(w) for w in weights]

        return new

    def to_xml(self):
        element = ET.Element(self.tag_name)
        columns = 10
        text = []

        for index, weight in enumerate(self.value):
            text.append(str(weight))
            if index < len(self.value) - 1:
                text.append(" ")
            if (index + 1) % columns == 0:
                text.append("\n")

        element.text = "".join(text)

        return element


class FrameFilter(ElementTree):
    tag_name = "FrameFilter"

    def __init__(self):
        super().__init__()
        self.name = TextPropertyRequired("Name", "")
        self.entries = FrameFilterEntriesList()
        self.weights = FrameFilterWeights()


class FrameFilterDictionary(MutableSequence, Element):
    tag_name = "FrameFilterDictionary"

    def __init__(self, value=None):
        super().__init__()
        self._value = value or []

    def __getitem__(self, name):
        return self._value[name]

    def __setitem__(self, key, value):
        self._value[key] = value

    def __delitem__(self, key):
        del self._value[key]

    def __iter__(self):
        return iter(self._value)

    def __len__(self):
        return len(self._value)

    def insert(self, index, value):
        self._value.insert(index, value)

    def sort(self, key):
        self._value.sort(key=key)

    @classmethod
    def from_xml(cls, element: ET.Element):
        new = cls()
        new.tag_name = "Item"
        children = element.findall(new.tag_name)

        for child in children:
            frame_filter = FrameFilter.from_xml(child)
            new.append(frame_filter)

        return new

    def to_xml(self):
        element = ET.Element(self.tag_name)
        for frame_filter in self._value:
            if isinstance(frame_filter, FrameFilter):
                frame_filter.tag_name = "Item"
                element.append(frame_filter.to_xml())
            else:
                raise TypeError(
                    f"{type(self).__name__}s can only hold '{FrameFilter.__name__}' objects, not '{type(frame_filter)}'!")

        return element
