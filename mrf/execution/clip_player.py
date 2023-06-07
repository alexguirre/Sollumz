import bpy
import bl_math
from ...sollumz_properties import SollumType
from .frame_buffer import FrameBuffer


class ClipPlayer:
    def __init__(self, clip_obj, armature_obj):
        if clip_obj.sollum_type != SollumType.CLIP:
            raise Exception("clip_obj is not a clip")

        clip_properties = clip_obj.clip_properties
        self.clip_obj = clip_obj
        self.clip_dictionary = clip_obj.parent.parent
        self.frame_curr = 0
        self.frame_count = round(clip_properties.duration * bpy.context.scene.render.fps)
        num_bones = len(armature_obj.pose.bones)
        self.frames = [FrameBuffer(num_bones) for _ in range(self.frame_count)]
        # TODO: set framebuffer from original pose of armature

        bone_name_to_index = {}
        bone_index = 0
        for bone in armature_obj.pose.bones:
            bone_name_to_index[bone.name] = bone_index
            bone_index += 1

        # cache all the clip animation frames
        groups = {}
        for clip_animation in clip_properties.animations:
            if clip_animation.animation is None:
                continue

            animation_properties = clip_animation.animation.animation_properties

            start_frames = clip_animation.start_frame
            end_frames = clip_animation.end_frame

            actions = []

            if animation_properties.base_action is not None:
                actions.append(animation_properties.base_action)

            if animation_properties.root_motion_location_action is not None:
                actions.append(animation_properties.root_motion_location_action)

            for action in actions:
                if action.name not in groups:
                    groups[action.name] = []

                group = groups[action.name]

                group.append({
                    "name": clip_properties.hash,
                    "start_frames": start_frames,
                    "end_frames": end_frames,
                    "action": action,
                })

        tmp_buffer = FrameBuffer(num_bones)
        for group_name, clips in groups.items():
            for clip in clips:
                action_frame_start = clip["start_frames"]
                action_frame_end = clip["end_frames"]
                action = clip["action"]

                curves = []
                for fcurve in action.fcurves:
                    # 'pose.bones["SKEL_ROOT"].location' -> ['pose.bones[', 'SKEL_ROOT', '].location']
                    data_path = fcurve.data_path.split('"')
                    assert len(data_path) == 3
                    assert data_path[0] == "pose.bones["
                    bone_name = data_path[1]
                    bone_index = bone_name_to_index[bone_name]
                    data_type = data_path[2]
                    if data_type == "].location":
                        data_type = 0
                    elif data_type == "].rotation_quaternion":
                        data_type = 1
                    elif data_type == "].scale":
                        data_type = 2

                    curves.append((fcurve, bone_index, data_type))

                for frame in range(self.frame_count):
                    tmp_buffer.make_identity()
                    frame_interpolated = bl_math.lerp(action_frame_start, action_frame_end, frame / self.frame_count)

                    for fcurve, bone_index, data_type in curves:
                        index = fcurve.array_index
                        val = fcurve.evaluate(frame_interpolated)

                        if data_type == 0:
                            tmp_buffer.position_data[bone_index][index] = val
                        elif data_type == 1:
                            tmp_buffer.rotation_data[bone_index][index] = val
                        elif data_type == 2:
                            tmp_buffer.scale_data[bone_index][index] = val

                    if "_root_motion_location" in group_name:
                        self.frames[frame].add(tmp_buffer)
                    elif "_root_motion_rotation" in group_name:
                        self.frames[frame].multiply(tmp_buffer)
                    elif "_base" in group_name:
                        self.frames[frame].combine(tmp_buffer)

    @property
    def phase(self):
        return self.frame_curr / (self.frame_count - 1)

    @phase.setter
    def phase(self, value):
        self.frame_curr = round((self.frame_count - 1) * value)

    def frame_update(self):
        # TODO: use time or phase to determine frame and interpolate between frames
        if self.frame_curr >= self.frame_count:
            self.frame_curr = 0

        frame = self.frames[self.frame_curr].copy()  # TODO: may want to receive a buffer to write to instead so it can be reused
        self.frame_curr += 1
        return frame
