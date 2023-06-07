import bpy
import bl_math
from ..nodes.node_tree import NetworkTree
from ...tools.blenderhelper import get_armature_obj
from .clip_player import ClipPlayer

class NetworkPlayer:
    def __init__(self, network: NetworkTree):
        self.network = network
        self.armature = None
        self.armature_obj = None
        self.frame_changed_handler = lambda scene: self.frame_changed(scene)
        self.is_playing = False
        self.frame_curr = 0
        self.frame_prev = 0
        self.tmp = True

        self.clip_player1 = None
        self.clip_player2 = None

    def set_armature(self, armature):
        self.armature = armature
        self.armature_obj = get_armature_obj(armature)

        clip_obj1 = bpy.data.objects["sweep_high_full"]
        clip_obj2 = bpy.data.objects["sweep_med_full"]
        self.clip_player1 = ClipPlayer(clip_obj1, self.armature_obj)
        self.clip_player2 = ClipPlayer(clip_obj2, self.armature_obj)

    def play(self):
        if self.is_playing:
            return
        self.frame_curr = 0
        self.frame_prev = 0
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = 1048574  # max frame count
        bpy.context.scene.frame_set(0)
        bpy.app.handlers.frame_change_pre.append(self.frame_changed_handler)
        # bpy.ops.screen.animation_play()
        self.is_playing = True

    def stop(self):
        if not self.is_playing:
            return
        bpy.app.handlers.frame_change_pre.remove(self.frame_changed_handler)
        # bpy.ops.screen.animation_cancel()
        self.is_playing = False

    def frame_update(self):
        self.clip_player1.phase = self.network.debug_phase
        self.clip_player2.phase = self.network.debug_phase
        frame1 = self.clip_player1.frame_update()
        frame2 = self.clip_player2.frame_update()
        frame1.blend(frame2, self.network.debug_blend_weight)
        frame1.apply_to_armature_obj(self.armature_obj)

    def frame_changed(self, scene):
        frame = scene.frame_current
        if frame <= self.frame_prev:  # backwards execution is not supported
            return

        # print("NetworkPlayer[frame {}]".format(frame))
        num_updates = frame - self.frame_prev
        for i in range(num_updates):
            self.frame_curr += 1
            self.frame_update()
            self.frame_prev = self.frame_curr
