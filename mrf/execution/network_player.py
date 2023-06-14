import bpy
import bl_math
from ..nodes.node_tree import NetworkTree
from ...tools.blenderhelper import get_armature_obj
from .clip_player import ClipPlayer
from .animation_tree_player import AnimationTreePlayer
from .state_machine_player import StateMachinePlayer

class NetworkPlayer:
    def __init__(self, network: NetworkTree):
        assert network.network_tree_type == "ROOT"

        self.network = network
        self.tree_to_preview = None  # ANIMATION_TREE or STATE_MACHINE
        self.tree_player = None  # AnimationTreePlayer or StateMachinePlayer
        self.armature = None
        self.armature_obj = None
        self.frame_changed_handler = lambda scene: self.frame_changed(scene)
        self.is_playing = False
        self.frame_curr = 0
        self.frame_prev = 0

        self.clip_player1 = None
        self.clip_player2 = None

    def set_animation_tree_to_preview(self, animation_tree: NetworkTree):
        """Set to preview a specific animation tree instead of the whole MoVE network."""
        assert animation_tree.network_tree_type == "ANIMATION_TREE"
        assert animation_tree.network_root == self.network
        assert not self.is_playing, "Cannot change animation tree while playing."
        assert self.armature is not None and self.armature_obj is not None, "Armature must be set."

        self.tree_to_preview = animation_tree
        self.tree_player = AnimationTreePlayer(animation_tree, self.armature_obj)

    def clear_animation_tree_to_preview(self):
        assert not self.is_playing, "Cannot change animation tree while playing."

        self.tree_to_preview = None
        self.tree_player = None


    def set_state_machine_to_preview(self, state_machine: NetworkTree):
        """Set to preview a specific state machine instead of the whole MoVE network."""
        assert state_machine.network_tree_type == "STATE_MACHINE"
        assert state_machine.network_root == self.network
        assert not self.is_playing, "Cannot change state machine while playing."
        assert self.armature is not None and self.armature_obj is not None, "Armature must be set."

        self.tree_to_preview = state_machine
        self.tree_player = StateMachinePlayer(state_machine, self.armature_obj)

    def clear_state_machine_to_preview(self):
        assert not self.is_playing, "Cannot change state machine while playing."

        self.tree_to_preview = None
        self.tree_player = None

    def set_armature(self, armature):
        assert not self.is_playing, "Cannot change armature while playing."

        self.armature = armature
        self.armature_obj = get_armature_obj(armature)

        clip_obj1 = bpy.data.objects["sweep_high_full"]
        clip_obj2 = bpy.data.objects["sweep_med_full"]
        self.clip_player1 = ClipPlayer(self.armature_obj)
        self.clip_player1.clip = clip_obj1
        self.clip_player2 = ClipPlayer(self.armature_obj)
        self.clip_player2.clip = clip_obj2

    def play(self):
        assert self.armature is not None, "Armature must be set."

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
        delta_time = 1 / bpy.context.scene.render.fps

        # self.clip_player1.phase = self.network.debug_phase
        # self.clip_player2.phase = self.network.debug_phase
        # frame1 = self.clip_player1.update(0.0)
        # frame2 = self.clip_player2.update(0.0)
        # frame1.blend(frame2, self.network.debug_blend_weight)
        # frame1.apply_to_armature_obj(self.armature_obj)

        # self.clip_player1.rate = self.network.debug_rate
        # frame1 = self.clip_player1.update(delta_time)
        # frame1.apply_to_armature_obj(self.armature_obj)

        frame = self.tree_player.update(delta_time)
        frame.apply_to_armature_obj(self.armature_obj)

    def frame_changed(self, scene):
        frame = scene.frame_current
        if frame <= self.frame_prev:  # backwards execution is not supported
            return

        print(f"============ NetworkPlayer[frame {frame}] ============")
        num_updates = frame - self.frame_prev
        for i in range(num_updates):
            self.frame_curr += 1
            self.frame_update()
            self.frame_prev = self.frame_curr
        print("======================================================")
