import os

import bpy
from ..cwxml.mrf import MRF, MoveNetwork
from ..tools.blenderhelper import create_empty_object
from ..sollumz_properties import SollumType
from .properties import MoveNetworkProperties, MoveNetworkBitProperties


def import_mrf(filepath: str):
    mrf_xml = MRF.from_xml_file(filepath)
    MRF.write_xml(mrf_xml, "D:\\re\\gta5\\test.mrf.xml")
    move_network_to_obj(mrf_xml, os.path.basename(filepath.replace(MRF.file_extension, "")))


def move_network_to_obj(mrf_xml: MoveNetwork, name: str):
    move_network_obj = create_empty_object(SollumType.MOVE_NETWORK, name)

    set_move_network_properties(mrf_xml, move_network_obj)


def set_move_network_properties(mrf_xml: MoveNetwork, obj: bpy.types.Object):
    obj.move_network_properties.test = 1234
    # obj.move_network_properties.triggers = mrf_xml.triggers
    # obj.move_network_properties.flags = mrf_xml.flags
    # obj.move_network_properties.root_state = mrf_xml.root_state

    for trigger in mrf_xml.triggers:
        trigger_props = obj.move_network_properties.triggers.add()
        trigger_props.name = trigger.name
        trigger_props.bit_position = trigger.bit_position
    for flag in mrf_xml.flags:
        flag_props = obj.move_network_properties.flags.add()
        flag_props.name = flag.name
        flag_props.bit_position = flag.bit_position
