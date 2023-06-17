import bpy
import bl_math
import math
from ...sollumz_properties import SollumType
from .frame_buffer import FrameBuffer


class ClipPlayer:
    def __init__(self, armature_obj):
        self._clip_obj = None
        self.armature_obj = armature_obj
        self.num_bones = len(self.armature_obj.pose.bones)
        self.duration = 0.0
        self.time = 0.0
        self.rate = 1.0
        self.delta = 0.0  # TODO: handle delta value
        self.looped = False  # TODO: handle looped value
        self.frame_count = 0
        self.frames = []

    @property
    def clip(self):
        return self._clip_obj

    @clip.setter
    def clip(self, value):
        if value is None:
            self._clip_obj = None
            return

        assert value.sollum_type == SollumType.CLIP

        if value != self._clip_obj:
            self._clip_obj = value
            self._cache_animation_frames()

    @property
    def phase(self):
        return self.time / self.duration if self.duration != 0.0 else 0.0

    @phase.setter
    def phase(self, value):
        self.time = self.duration * value

    def update(self, delta_time):
        if self._clip_obj is None:
            return FrameBuffer(self.num_bones)

        self.time += delta_time * self.rate
        frame_curr = (self.frame_count - 1) * self.phase
        frame_idx = math.floor(frame_curr) % self.frame_count
        frame = self.frames[frame_idx].copy()  # TODO: may want to receive a buffer to write to instead so it can be reused
        if frame_idx + 1 < self.frame_count:
            # subframe interpolation
            frame_next = self.frames[(frame_idx + 1) % self.frame_count]
            subframe = frame_curr - math.floor(frame_curr)
            frame.blend(frame_next, subframe)
        return frame

    def _cache_animation_frames(self):
        assert self._clip_obj is not None

        clip_properties = self._clip_obj.clip_properties
        self.duration = clip_properties.duration
        self.frame_count = round(clip_properties.duration * bpy.context.scene.render.fps)
        self.frames = [FrameBuffer(self.num_bones) for _ in range(self.frame_count)]  # TODO: may want to reuse buffers

        bone_name_to_index = {}
        bone_index = 0
        for bone in self.armature_obj.pose.bones:
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

        tmp_buffer = FrameBuffer(self.num_bones)
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
                    tmp_buffer.make_invalid()
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

                    # on invalid elements the previous operations are no-ops,
                    # so we merge to replace invalid elements with valid ones
                    self.frames[frame].merge(tmp_buffer)
