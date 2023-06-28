import bpy
import bl_math
from ..nodes.node_tree import NetworkTree
from ...tools.blenderhelper import get_armature_obj
from .clip_player import ClipPlayer
from .expression_player import ExpressionPlayer
from .animation_tree_player import AnimationTreePlayer
from .state_machine_player import StateMachinePlayer
from .frame_buffer import FrameBuffer

from ...cwxml.yfd import YFD
from ...cwxml.yed import YED


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
        self.identity_frame = None

        self._expression_player = None

        frame_filter_dict_xml = YFD.from_xml_file("D:\\re\\gta5\\player.yfd.xml")
        self.frame_filter_dict = {}
        for frame_filter in frame_filter_dict_xml:
            self.frame_filter_dict[frame_filter.name] = frame_filter

        expr_dict_xml = YED.from_xml_file("D:\\re\\gta5\\yeds\\p_barriercrash_01_s.yed.xml")
        self.expr_dict = {}
        for expr in expr_dict_xml:
            self.expr_dict[expr.name] = expr

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
        self.identity_frame = FrameBuffer(len(self.armature_obj.pose.bones))
        self.identity_frame.make_identity()

        self._expression_player = ExpressionPlayer(self.armature_obj, self.expr_dict["pack:/p_barriercrash_01_s.expr"])

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

        frame = FrameBuffer(len(self.armature_obj.pose.bones))
        frame.from_armature_obj(self.armature_obj)
        self._expression_player.update(delta_time, frame)
        frame.apply_to_armature_obj(self.armature_obj)

        # frame = self.tree_player.update(delta_time)
        # frame.merge(self.identity_frame)  # use identity as base for bones not set by the tree
        # frame.apply_to_armature_obj(self.armature_obj)

    def frame_changed(self, scene):
        frame = scene.frame_current
        if frame <= self.frame_prev:  # backwards execution is not supported
            return

        # print(f"============ NetworkPlayer[frame {frame}] ============")
        num_updates = frame - self.frame_prev
        for i in range(num_updates):
            self.frame_curr += 1
            self.frame_update()
            self.frame_prev = self.frame_curr
        # print("======================================================")

        bpy.context.area.tag_redraw()  # force redraw to update the active state indicators
