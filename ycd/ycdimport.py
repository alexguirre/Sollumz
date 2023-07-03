import os
import bpy
from mathutils import Vector, Quaternion, Matrix
from ..cwxml.clipsdictionary import YCD
from ..sollumz_properties import SOLLUMZ_UI_NAMES, SollumType
from ..tools.blenderhelper import build_bone_map, get_armature_obj
from ..tools.animationhelper import is_ped_bone_tag
from ..tools.utils import list_index_exists
from .properties import AnimationTrackToPropertyName


def create_anim_obj(type):
    anim_obj = bpy.data.objects.new(SOLLUMZ_UI_NAMES[type], None)
    anim_obj.empty_display_size = 0
    anim_obj.sollum_type = type
    bpy.context.collection.objects.link(anim_obj)

    return anim_obj


def insert_action_data(actions_data, bone_name, track, data):
    if bone_name not in actions_data:
        actions_data[bone_name] = {}

    if track not in actions_data[bone_name]:
        actions_data[bone_name][track] = []

    actions_data[bone_name][track].append(data)


def get_values_from_sequence_data(sequence_data, frame_id):
    channel_values = []

    for i in range(len(sequence_data.channels)):
        while len(channel_values) <= i:
            channel_values.append(None)

        channel = sequence_data.channels[i]

        if channel is not None:
            channel_values[i] = channel.get_value(frame_id, channel_values)

    return channel_values


def get_location_from_sequence_data(sequence_data, frame_id):
    channel_values = get_values_from_sequence_data(sequence_data, frame_id)

    if len(channel_values) == 1:
        location = channel_values[0]
    else:
        location = Vector([
            channel_values[0],
            channel_values[1],
            channel_values[2],
        ])

    return location


def get_quaternion_from_sequence_data(sequence_data, frame_id):
    channel_values = get_values_from_sequence_data(sequence_data, frame_id)

    if len(channel_values) == 1:
        rotation = channel_values[0]
    else:
        if len(sequence_data.channels) <= 4:
            for channel in sequence_data.channels:
                if channel.type == "CachedQuaternion1" or channel.type == "CachedQuaternion2":
                    cached_value = channel.get_value(frame_id, channel_values)

                    if channel.quat_index == 0:
                        channel_values = [
                            cached_value, channel_values[0], channel_values[1], channel_values[2]]
                    elif channel.quat_index == 1:
                        channel_values = [
                            channel_values[0], cached_value, channel_values[1], channel_values[2]]
                    elif channel.quat_index == 2:
                        channel_values = [
                            channel_values[0], channel_values[1], cached_value, channel_values[2]]
                    elif channel.quat_index == 3:
                        channel_values = [
                            channel_values[0], channel_values[1], channel_values[2], cached_value]

            if channel.type == "CachedQuaternion2":
                rotation = Quaternion(
                    (channel_values[0], channel_values[1], channel_values[2], channel_values[3]))
            else:
                rotation = Quaternion(
                    (channel_values[3], channel_values[0], channel_values[1], channel_values[2]))
        else:
            rotation = Quaternion(
                (channel_values[3], channel_values[0], channel_values[1], channel_values[2]))

    return rotation


def combine_sequences_and_build_action_data(animation):
    # def _add_pseudo_bone(bone_id):
    #     bone_name = f"#{bone_id}"
    #     bpy.context.view_layer.objects.active = armature_obj
    #     bpy.ops.object.mode_set(mode="EDIT")
    #     edit_bone = armature_obj.data.edit_bones.new(bone_name)
    #     edit_bone.head = (0, 0, 0)
    #     edit_bone.tail = (0, 0.05, 0)
    #     edit_bone.matrix = Matrix.Identity(4)
    #     bpy.ops.object.mode_set(mode="OBJECT")
    #     bl_bone = armature_obj.pose.bones[bone_name].bone
    #     bl_bone.bone_properties.tag = bone_id
    #     return bone_name

    # bone_map = build_bone_map(armature_obj)

    sequence_frame_limit = animation.sequence_frame_limit

    if len(animation.sequences) <= 1:
        sequence_frame_limit = animation.frame_count + 30

    action_data = {}
    track_to_format = {}

    for frame_id in range(0, animation.frame_count):
        sequence_index = int(frame_id / (sequence_frame_limit))
        sequence_frame = frame_id % (sequence_frame_limit)

        if sequence_index >= len(animation.sequences):
            sequence_index = len(animation.sequences) - 1

        sequence = animation.sequences[sequence_index]

        for sequence_data_index, sequence_data in enumerate(sequence.sequence_data):
            bone_data = animation.bone_ids[sequence_data_index]
            bone_id = bone_data.bone_id

            if bone_data is None:
                continue

            bone_name = f"#{bone_id}"
            track = bone_data.track
            format = bone_data.unk0
            track_to_format[track] = format
            if format == 0:  # vector3
                location = get_location_from_sequence_data(sequence_data, sequence_frame)
                insert_action_data(action_data, bone_name, track, location)
            elif format == 1:  # quaternion
                rotation = get_quaternion_from_sequence_data(sequence_data, sequence_frame)
                insert_action_data(action_data, bone_name, track, rotation)
            elif format == 2:  # float
                value = get_values_from_sequence_data(sequence_data, sequence_frame)[0]
                insert_action_data(action_data, bone_name, track, value)

    return action_data, track_to_format


def get_data_path_for_track(track, bone_name):
    if bone_name is not None:
        base = f'pose.bones["{bone_name}"].'
        base_t = f'pose.bones["{bone_name}"].animation_tracks_'
    else:
        base = ""
        base_t = "animation_tracks."

    if track == 0:
        return f'{base}location'
    elif track == 1:
        return f'{base}rotation_quaternion'
    elif track == 2:
        return f'{base}scale'
    elif track == 5:  # only the root bone should have the root motion tracks, so `delta_` properties should be fine
        return "delta_location"
    elif track == 6:
        return "delta_rotation_quaternion"
    elif track == 7:  # for cameras
        return f'location'
    elif track == 8:
        return f'rotation_quaternion'
    else:
        return f'{base_t}{AnimationTrackToPropertyName[track]}'


def apply_action_data_to_action(action_data, action, frame_count, track_to_format):
    frames_ids = [*range(frame_count)]

    for bone_name, bones_data in action_data.items():
        group_item = action.groups.new(bone_name)
        for track_id, frames_data in bones_data.items():
            format = track_to_format[track_id]
            data_path = get_data_path_for_track(track_id, bone_name)
            if format == 0:  # vector3
                vec_tracks_x = list(map(lambda vec: vec.x, frames_data))
                vec_tracks_y = list(map(lambda vec: vec.y, frames_data))
                vec_tracks_z = list(map(lambda vec: vec.z, frames_data))

                vec_curve_x = action.fcurves.new(data_path=data_path, index=0)
                vec_curve_y = action.fcurves.new(data_path=data_path, index=1)
                vec_curve_z = action.fcurves.new(data_path=data_path, index=2)

                vec_curve_x.group = group_item
                vec_curve_y.group = group_item
                vec_curve_z.group = group_item

                vec_curve_x.keyframe_points.add(len(frames_data))
                vec_curve_y.keyframe_points.add(len(frames_data))
                vec_curve_z.keyframe_points.add(len(frames_data))

                vec_curve_x.keyframe_points.foreach_set(
                    "co", [x for co in zip(frames_ids, vec_tracks_x) for x in co])
                vec_curve_y.keyframe_points.foreach_set(
                    "co", [x for co in zip(frames_ids, vec_tracks_y) for x in co])
                vec_curve_z.keyframe_points.foreach_set(
                    "co", [x for co in zip(frames_ids, vec_tracks_z) for x in co])

                vec_curve_x.update()
                vec_curve_y.update()
                vec_curve_z.update()
            elif format == 1:  # quaternion
                quat_tracks_x = list(map(lambda rotation: rotation.x, frames_data))
                quat_tracks_y = list(map(lambda rotation: rotation.y, frames_data))
                quat_tracks_z = list(map(lambda rotation: rotation.z, frames_data))
                quat_tracks_w = list(map(lambda rotation: rotation.w, frames_data))

                quat_curve_w = action.fcurves.new(data_path=data_path, index=0)
                quat_curve_x = action.fcurves.new(data_path=data_path, index=1)
                quat_curve_y = action.fcurves.new(data_path=data_path, index=2)
                quat_curve_z = action.fcurves.new(data_path=data_path, index=3)

                quat_curve_w.group = group_item
                quat_curve_x.group = group_item
                quat_curve_y.group = group_item
                quat_curve_z.group = group_item

                quat_curve_w.keyframe_points.add(len(frames_data))
                quat_curve_x.keyframe_points.add(len(frames_data))
                quat_curve_y.keyframe_points.add(len(frames_data))
                quat_curve_z.keyframe_points.add(len(frames_data))

                quat_curve_w.keyframe_points.foreach_set(
                    "co", [x for co in zip(frames_ids, quat_tracks_w) for x in co])
                quat_curve_x.keyframe_points.foreach_set(
                    "co", [x for co in zip(frames_ids, quat_tracks_x) for x in co])
                quat_curve_y.keyframe_points.foreach_set(
                    "co", [x for co in zip(frames_ids, quat_tracks_y) for x in co])
                quat_curve_z.keyframe_points.foreach_set(
                    "co", [x for co in zip(frames_ids, quat_tracks_z) for x in co])

                quat_curve_w.update()
                quat_curve_x.update()
                quat_curve_y.update()
                quat_curve_z.update()
            elif format == 2:  # float
                value_curve = action.fcurves.new(data_path=data_path)
                value_curve.group = group_item

                value_curve.keyframe_points.add(len(frames_data))
                value_curve.keyframe_points.foreach_set("co", [x for co in zip(frames_ids, frames_data) for x in co])

                value_curve.update()


def action_data_to_action(action_name, action_data, frame_count, track_to_format):
    action = bpy.data.actions.new(f"{action_name}_action")
    apply_action_data_to_action(action_data, action, frame_count, track_to_format)
    return action


def animation_to_obj(animation):
    animation_obj = create_anim_obj(SollumType.ANIMATION)

    animation_obj.name = animation.hash
    animation_obj.animation_properties.hash = animation.hash
    animation_obj.animation_properties.frame_count = animation.frame_count

    action_data, track_to_format = combine_sequences_and_build_action_data(animation)
    animation_obj.animation_properties.action = action_data_to_action(animation.hash, action_data,
                                                                      animation.frame_count, track_to_format)

    return animation_obj


def clip_to_obj(clip, animations_map, animations_obj_map):
    clip_obj = create_anim_obj(SollumType.CLIP)

    clip_obj.name = clip.hash
    clip_obj.clip_properties.hash = clip.hash
    clip_obj.clip_properties.name = clip.name
    clip_obj.clip_properties.animations.clear()

    if clip.type == "Animation":
        animation_data = animations_map[clip.animation_hash]

        clip_obj.clip_properties.duration = clip.end_time - clip.start_time

        clip_animation = clip_obj.clip_properties.animations.add()
        clip_animation.animation = animations_obj_map[clip.animation_hash]
        clip_animation.start_frame = int(
            (clip.start_time / animation_data.duration) * animation_data.frame_count)
        clip_animation.end_frame = int(
            (clip.end_time / animation_data.duration) * animation_data.frame_count)
    elif clip.type == "AnimationList":
        clip_obj.clip_properties.duration = clip.duration

        for animation in clip.animations:
            animation_data = animations_map[animation.animation_hash]

            clip_animation = clip_obj.clip_properties.animations.add()
            clip_animation.animation = animations_obj_map[animation.animation_hash]
            clip_animation.start_frame = int(
                (animation.start_time / animation_data.duration) * animation_data.frame_count)
            clip_animation.end_frame = int(
                (animation.end_time / animation_data.duration) * animation_data.frame_count)

    return clip_obj


def create_clip_dictionary_template(name):
    clip_dictionary_obj = create_anim_obj(SollumType.CLIP_DICTIONARY)
    clips_obj = create_anim_obj(SollumType.CLIPS)
    animations_obj = create_anim_obj(SollumType.ANIMATIONS)

    clip_dictionary_obj.name = name

    clips_obj.parent = clip_dictionary_obj
    animations_obj.parent = clip_dictionary_obj

    return clip_dictionary_obj, clips_obj, animations_obj


def clip_dictionary_to_obj(clip_dictionary, name):
    _, clips_obj, animations_obj = create_clip_dictionary_template(name)

    animations_map = {}
    animations_obj_map = {}

    for animation in clip_dictionary.animations:
        animations_map[animation.hash] = animation

        animation_obj = animation_to_obj(animation)
        animation_obj.parent = animations_obj

        animations_obj_map[animation.hash] = animation_obj

    for clip in clip_dictionary.clips:
        clip.name = clip.name.replace("pack:/", "")
        clip_obj = clip_to_obj(clip, animations_map, animations_obj_map)
        clip_obj.parent = clips_obj


def import_ycd(export_op, filepath, import_settings):
    # if import_settings.selected_armature == -1 or not list_index_exists(bpy.data.armatures, import_settings.selected_armature):
    #     # export_op.warning("Selected target skeleton not found.")
    #     armature_obj = None
    # else:
    #     armature = bpy.data.armatures[import_settings.selected_armature]
    #     armature_obj = get_armature_obj(armature)

    ycd_xml = YCD.from_xml_file(filepath)

    # animation_type = bpy.context.scene.create_animation_type
    # if animation_type == "UV":
    #     export_op.warning("UV import is not supported. Change the animation type under Animation Tools panel")
    #     return

    clip_dictionary_to_obj(
        ycd_xml,
        os.path.basename(
            filepath.replace(YCD.file_extension, "")
        )
    )
