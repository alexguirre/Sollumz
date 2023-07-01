import bpy

from ..sollumz_helper import SOLLUMZ_OT_base
from ..sollumz_properties import SollumType
from ..tools.blenderhelper import find_child_by_type, get_armature_obj
from .ycdimport import create_clip_dictionary_template, create_anim_obj


class SOLLUMZ_OT_clip_apply_nla(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.anim_apply_nla"
    bl_label = "Apply NLA"
    bl_description = "Applies clip as a Nonlinear Animation for a quick preview"

    def run(self, context):
        if len(bpy.context.selected_objects) <= 0:
            return {"FINISHED"}

        clip_obj = bpy.context.selected_objects[0]

        if clip_obj.sollum_type != SollumType.CLIP:
            return {"FINISHED"}

        clip_properties = clip_obj.clip_properties
        if len(clip_properties.animations) <= 0:
            return {"FINISHED"}

        clip_dictionary = clip_obj.parent.parent
        # TODO: animation may be None, or not all animations have the same target/are filled in
        target = clip_properties.animations[0].animation.animation_properties.target_id
        if target is None:
            return {"FINISHED"}

        if isinstance(target, bpy.types.Armature):
            target = get_armature_obj(target)

        if target is None:
            return {"FINISHED"}

        clip_frame_count = round(clip_properties.duration * bpy.context.scene.render.fps)

        groups = {}

        for clip_animation in clip_properties.animations:
            if clip_animation.animation is None:
                continue

            animation_properties = clip_animation.animation.animation_properties

            start_frames = clip_animation.start_frame
            end_frames = clip_animation.end_frame

            action = animation_properties.action

            if action.name not in groups:
                groups[action.name] = []

            group = groups[action.name]

            group.append({
                "name": clip_properties.hash,
                "start_frames": start_frames,
                "end_frames": end_frames,
                "action": action,
            })

        if target.animation_data is None:
            target.animation_data_create()

        for nla_track in target.animation_data.nla_tracks:
            target.animation_data.nla_tracks.remove(nla_track)

        for group_name, clips in groups.items():
            track = target.animation_data.nla_tracks.new()
            track.name = group_name

            for clip in clips:
                action_frames_count = clip["end_frames"] - clip["start_frames"]

                nla_strip = track.strips.new(clip["name"], 0, clip["action"])
                nla_strip.frame_start = 0
                nla_strip.frame_end = clip_frame_count

                bpy.context.scene.frame_start = 0
                bpy.context.scene.frame_end = int(nla_strip.frame_end)

                nla_strip.blend_type = "COMBINE"
                nla_strip.extrapolation = "NOTHING"
                nla_strip.name = clip["name"]

                nla_strip.scale = clip_frame_count / action_frames_count
                nla_strip.action_frame_start = clip["start_frames"]
                nla_strip.action_frame_end = clip["end_frames"]

        return {"FINISHED"}


class SOLLUMZ_OT_clip_new_animation(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.anim_new_animation"
    bl_label = "Add a new animation"
    bl_description = "Adds a new animation entry to the clip dictionary"

    def run(self, context):
        if len(bpy.context.selected_objects) <= 0:
            return {"FINISHED"}

        active_object = bpy.context.selected_objects[0]

        if active_object.sollum_type != SollumType.CLIP:
            return {"FINISHED"}

        clip_properties = active_object.clip_properties

        clip_properties.animations.add()

        return {"FINISHED"}


class SOLLUMZ_OT_clip_delete_animation(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.anim_delete_animation"
    bl_label = "Delete animation"

    animation_index: bpy.props.IntProperty(name="animation_index")

    def run(self, context):
        if len(bpy.context.selected_objects) <= 0:
            return {"FINISHED"}

        active_object = bpy.context.selected_objects[0]

        if active_object.sollum_type != SollumType.CLIP:
            return {"FINISHED"}

        clip_properties = active_object.clip_properties

        clip_properties.animations.remove(self.animation_index)

        return {"FINISHED"}


class SOLLUMZ_OT_create_clip_dictionary(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.crate_clip_dictionary"
    bl_label = "Create clip dictionary template"

    def run(self, context):
        if len(bpy.context.selected_objects) <= 0:
            return {"FINISHED"}

        active_object = bpy.context.selected_objects[0]

        create_clip_dictionary_template("Clip Dictionary", active_object, anim_type)

        return {"FINISHED"}


class SOLLUMZ_OT_create_clip(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.crate_clip"
    bl_label = "Create clip"

    def run(self, context):
        if len(bpy.context.selected_objects) <= 0:
            return {"FINISHED"}

        active_object = bpy.context.selected_objects[0]

        clips_obj = None

        if active_object.sollum_type == SollumType.CLIP:
            clips_obj = active_object.parent
        elif active_object.sollum_type == SollumType.ANIMATION:
            clip_dictionary_obj = active_object.parent.parent

            clips_obj = find_child_by_type(
                clip_dictionary_obj, SollumType.CLIPS)
        elif active_object.sollum_type == SollumType.CLIPS:
            clips_obj = active_object
        elif active_object.sollum_type == SollumType.ANIMATIONS:
            clip_dictionary_obj = active_object.parent

            clips_obj = find_child_by_type(
                clip_dictionary_obj, SollumType.CLIPS)
        elif active_object.sollum_type == SollumType.CLIP_DICTIONARY:
            clip_dictionary_obj = active_object

            clips_obj = find_child_by_type(
                clip_dictionary_obj, SollumType.CLIPS)

        if clips_obj is not None:
            animation_obj = create_anim_obj(SollumType.CLIP)

            animation_obj.parent = clips_obj

        return {"FINISHED"}


class SOLLUMZ_OT_create_animation(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.crate_animation"
    bl_label = "Create animation"

    def run(self, context):
        if len(bpy.context.selected_objects) <= 0:
            return {"FINISHED"}

        active_object = bpy.context.selected_objects[0]

        animations_obj = None

        if active_object.sollum_type == SollumType.CLIP:
            clip_dictionary_obj = active_object.parent.parent

            animations_obj = find_child_by_type(
                clip_dictionary_obj, SollumType.ANIMATIONS)
        elif active_object.sollum_type == SollumType.ANIMATION:
            animations_obj = active_object.parent
        elif active_object.sollum_type == SollumType.CLIPS:
            clip_dictionary_obj = active_object.parent

            animations_obj = find_child_by_type(
                clip_dictionary_obj, SollumType.ANIMATIONS)
        elif active_object.sollum_type == SollumType.ANIMATIONS:
            animations_obj = active_object
        elif active_object.sollum_type == SollumType.CLIP_DICTIONARY:
            clip_dictionary_obj = active_object

            animations_obj = find_child_by_type(
                clip_dictionary_obj, SollumType.ANIMATIONS)

        if animations_obj is not None:
            animation_obj = create_anim_obj(SollumType.ANIMATION)

            animation_obj.parent = animations_obj

        return {"FINISHED"}


class SOLLUMZ_OT_animation_fill(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.animation_fill"
    bl_label = "Fill animation data"

    def run(self, context):
        if len(bpy.context.selected_objects) <= 0:
            return {"FINISHED"}

        active_object = bpy.context.selected_objects[0]

        animation_properties = active_object.animation_properties

        action_list = []

        if animation_properties.base_action:
            action_list.append(animation_properties.base_action.frame_range)

        if animation_properties.root_motion_location_action:
            action_list.append(
                animation_properties.root_motion_location_action.frame_range)

        if animation_properties.root_motion_rotation_action:
            action_list.append(
                animation_properties.root_motion_rotation_action.frame_range)

        frames = (
            sorted(set([item for sublist in action_list for item in sublist])))

        start_frame = frames[0]
        end_frame = frames[-1]

        frame_count = end_frame - start_frame

        animation_properties.frame_count = int(frame_count)

        return {"FINISHED"}


class SOLLUMZ_OT_create_uv_anim_node(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.create_uv_anim_node"
    bl_label = "Add UV node to material"

    def run(self, context):
        if len(bpy.context.selected_objects) <= 0:
            return {"FINISHED"}

        active_object = bpy.context.selected_objects[0]

        active_material = active_object.active_material
        if active_material.sollum_type == "sollumz_material_none":
            self.report({"ERROR"}, "Selected material is not a Sollumz shader")
            return {"FINISHED"}
        
        mat_nodetree = active_material.node_tree
        mat_nodes = mat_nodetree.nodes
        for node in mat_nodes:
            if node.type == "BSDF_PRINCIPLED":
                base_color_input = node.inputs[0].links[0]
                base_tex_node = base_color_input.from_node

                texnode_location = base_tex_node.location
                mathnode = mat_nodes.new("ShaderNodeVectorMath")
                mathnode.operation = "ADD"
                uvnode = mat_nodes.new("ShaderNodeUVMap")
                
                mathnode.location = (texnode_location[0]-250, 0)
                uvnode.location = (mathnode.location[0]-250, 0)
                
                mat_nodetree.links.new(base_tex_node.inputs[0], mathnode.outputs[0])
                mat_nodetree.links.new(mathnode.inputs[0], uvnode.outputs[0])
                self.report({"INFO"}, "Added UV animation link to selected material")
                break

        return {"FINISHED"}
