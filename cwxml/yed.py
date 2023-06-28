from xml.etree import ElementTree as ET
from .element import (
    Element,
    ElementTree,
    ElementProperty,
    ListPropertyRequired,
    TextPropertyRequired,
    ValueProperty,
    AttributeProperty,
    Vector4Property,
)
from collections.abc import MutableSequence


class YED:
    file_extension = ".yed.xml"

    @staticmethod
    def from_xml_file(filepath):
        return ExpressionDictionary.from_xml_file(filepath)

    @staticmethod
    def write_xml(expression_dictionary, filepath):
        return expression_dictionary.write_xml(filepath)


class ExpressionTrack(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.bone_id = ValueProperty("BoneId")
        self.track = ValueProperty("Track")
        self.format = ValueProperty("Format")
        self.unk_flag = ValueProperty("UnkFlag", False)


class ExpressionTracksList(ListPropertyRequired):
    list_type = ExpressionTrack
    tag_name = "Tracks"


class ExpressionInstr(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.type = AttributeProperty("type", self.type)


class ExpressionInstrBlend(ExpressionInstr):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        # TODO: ExpressionInstrBlend


class ExpressionInstrBone(ExpressionInstr):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.track_index = ValueProperty("TrackIndex")
        self.bone_id = ValueProperty("BoneId")
        self.track = ValueProperty("Track")
        self.format = ValueProperty("Format")
        self.component_index = ValueProperty("ComponentIndex")
        self.use_defaults = ValueProperty("UseDefaults", False)


class ExpressionInstrVariable(ExpressionInstr):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.variable = TextPropertyRequired("Variable", "")


class ExpressionInstrJump(ExpressionInstr):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.instruction_offset = ValueProperty("InstructionOffset", 0)


class ExpressionInstrFloat(ExpressionInstr):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.value = ValueProperty("Value", 0.0)


class ExpressionInstrVector(ExpressionInstr):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.value = Vector4Property("Value")


class ExpressionInstrSpring(ExpressionInstr):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        # TODO: ExpressionInstrSpring


class ExpressionInstrLookAt(ExpressionInstr):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        # TODO: ExpressionInstrLookAt


class ExpressionInstructionsList(ListPropertyRequired):
    list_type = ExpressionInstr
    tag_name = "Instructions"

    @staticmethod
    def from_xml(element: ET.Element):
        new = ExpressionInstructionsList()

        for child in element.iter():
            if "type" in child.attrib:
                instr_type = child.get("type")
                if instr_type in {"Pop", "Dup", "Push0", "Push1", "VectorAbs", "VectorNeg", "VectorRcp", "VectorSqrt",
                                  "VectorNeg3", "VectorSquare", "VectorDeg2Rad", "VectorRad2Deg", "VectorSaturate",
                                  "FromEuler", "ToEuler", "VectorAdd", "VectorSub", "VectorMul", "VectorMin",
                                  "VectorMax", "QuatMul", "VectorGreaterThan", "VectorLessThan", "VectorGreaterEqual",
                                  "VectorLessEqual", "VectorClamp", "VectorLerp", "VectorMad", "QuatSlerp", "ToVector",
                                  "PushTime", "VectorTransform", "PushDeltaTime", "VectorEqual", "VectorNotEqual"}:
                    new.value.append(ExpressionInstr.from_xml(child))
                elif instr_type in {"BlendVector", "BlendQuaternion"}:
                    new.value.append(ExpressionInstrBlend.from_xml(child))
                elif instr_type in {"TrackGet", "TrackGetComp", "TrackGetOffset", "TrackGetOffsetComp",
                                    "TrackGetBoneTransform", "TrackValid", "Unk23", "TrackSet", "TrackSetComp",
                                    "TrackSetOffset", "TrackSetOffsetComp", "TrackSetBoneTransform"}:
                    new.value.append(ExpressionInstrBone.from_xml(child))
                elif instr_type in {"GetVariable", "SetVariable"}:
                    new.value.append(ExpressionInstrVariable.from_xml(child))
                elif instr_type in {"Jump", "JumpIfTrue", "JumpIfFalse"}:
                    new.value.append(ExpressionInstrJump.from_xml(child))
                elif instr_type == "PushFloat":
                    new.value.append(ExpressionInstrFloat.from_xml(child))
                elif instr_type == "PushVector":
                    new.value.append(ExpressionInstrVector.from_xml(child))
                elif instr_type == "DefineSpring":
                    new.value.append(ExpressionInstrSpring.from_xml(child))
                elif instr_type == "LookAt":
                    new.value.append(ExpressionInstrLookAt.from_xml(child))
                else:
                    raise TypeError(f"Unknown instruction type: {instr_type}")

        return new


class ExpressionStream(ElementTree):
    tag_name = "Item"

    def __init__(self):
        super().__init__()
        self.name = TextPropertyRequired("Name", "")
        self.unk_0E = ValueProperty("Unk0E", 0)
        self.instructions = ExpressionInstructionsList()


class ExpressionStreamsList(ListPropertyRequired):
    list_type = ExpressionStream
    tag_name = "Streams"


class Expression(ElementTree):
    tag_name = "Expression"

    def __init__(self):
        super().__init__()
        self.name = TextPropertyRequired("Name", "")
        self.unk_7C = ValueProperty("Unk7C", 0)
        self.tracks = ExpressionTracksList()
        self.streams = ExpressionStreamsList()


class ExpressionDictionary(MutableSequence, Element):
    tag_name = "ExpressionDictionary"

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
            expr = Expression.from_xml(child)
            new.append(expr)

        return new

    def to_xml(self):
        element = ET.Element(self.tag_name)
        for expr in self._value:
            if isinstance(expr, Expression):
                expr.tag_name = "Item"
                element.append(expr.to_xml())
            else:
                raise TypeError(
                    f"{type(self).__name__}s can only hold '{Expression.__name__}' objects, not '{type(expr)}'!")

        return element
