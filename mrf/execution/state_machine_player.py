import bl_math
from ..nodes.nodes import *
from ..properties import SMTransitionProperties
from .frame_buffer import FrameBuffer
from .animation_tree_player import AnimationTreePlayer


class StateMachineContext:
    def __init__(self, network, state_machine, armature_obj):
        self.network = network
        self.state_machine = state_machine
        self.armature_obj = armature_obj
        self.num_bones = len(self.armature_obj.pose.bones)
        self.delta_time = 0.0
        self.active_state_time = 0.0

    def get_parameter(self, parameter_name):
        return self.network.network_parameters.get(parameter_name)

    def set_parameter(self, parameter_name, value):
        self.network.network_parameters.set(parameter_name, value)


class SMActiveTransition:
    def __init__(self, props: SMTransitionProperties,
                 from_state, duration,
                 state_machine_player, animation_tree_player):
        assert duration > 0.0
        assert state_machine_player is not None or animation_tree_player is not None, "Transition must have a player"

        self.props = props
        self.from_state = from_state
        self.duration = duration
        self.time = 0.0
        self.progress = 0.0
        self.state_machine_player = state_machine_player
        self.animation_tree_player = animation_tree_player

    def update(self, context: StateMachineContext):
        self.time += context.delta_time
        self.progress = bl_math.clamp(self.time / self.duration, 0.0, 1.0)
        if self.props.progress_parameter_name != "":
            context.set_parameter(self.props.progress_parameter_name, self.progress)

        if self.animation_tree_player is not None:
            return self.animation_tree_player.update(context.delta_time)
        elif self.state_machine_player is not None:
            return self.state_machine_player.update(context.delta_time)
        else:
            return FrameBuffer(context.num_bones)


class StateMachinePlayer:
    def __init__(self, state_machine, armature_obj):
        assert state_machine.network_tree_type == "STATE_MACHINE"

        self.state_machine = state_machine
        self.active_state_machine_player = None  # for state machines nodes
        self.active_animation_tree_player = None  # for state nodes
        self.active_state = None
        self.active_transitions = []
        self.context = StateMachineContext(state_machine.network_root, state_machine, armature_obj)

        start_node = self._get_start_node()
        assert start_node is not None, "SMNodeStart is required for state machines"
        start_state = state_machine.nodes[start_node.start_state]
        assert start_state is not None, "SMNodeStart must be connected to a state"
        self._change_active_state(start_state)

    def update(self, delta_time):
        self.context.delta_time = delta_time
        self.context.active_state_time += delta_time
        self._evaluate_transitions()
        return self._evaluate_active_state()

    def _change_active_state(self, new_state):
        self.active_state = new_state
        self.active_state_machine_player = None
        self.active_animation_tree_player = None
        self.context.active_state_time = 0.0
        if self.active_state.bl_idname == SMNodeState.bl_idname:
            self.active_animation_tree_player = AnimationTreePlayer(self.active_state.animation_tree,
                                                                    self.context.armature_obj)
        elif self.active_state.bl_idname == SMNodeStateMachine.bl_idname:
            self.active_state_machine_player = StateMachinePlayer(self.active_state.state_machine_tree,
                                                                  self.context.armature_obj)
        else:
            assert False, "Unknown state type"

    def _do_transition(self, transition: SMTransitionProperties):
        duration = transition.duration
        if transition.duration_parameter_name != "":
            duration_from_param = self.context.get_parameter(transition.duration_parameter_name)
            if duration_from_param is not None:
                duration = duration_from_param

        if duration > 0.0:
            new_active_transition = SMActiveTransition(transition,
                                                       self.active_state, duration,
                                                       self.active_state_machine_player,
                                                       self.active_animation_tree_player)
            self.active_transitions.append(new_active_transition)

        target_state = self.state_machine.nodes[transition.target_state]
        assert target_state is not None, "Transition target state must exist"
        self._change_active_state(target_state)

    def _evaluate_transitions(self):
        for t in self.active_state.transitions:
            do_transition = all(self._evaluate_condition(c) for c in t.conditions)
            if do_transition:
                self._do_transition(t)
                break

    def _evaluate_condition(self, condition: SMConditionProperties):
        t = condition.type
        if t == "ParameterInsideRange":
            value = float(self.context.get_parameter(condition.parameter))
            return condition.min < value < condition.max
        elif t == "ParameterOutsideRange":
            value = float(self.context.get_parameter(condition.parameter))
            return value < condition.min or condition.max < value
        elif t == "MoveNetworkTrigger":
            return False
        elif t == "MoveNetworkFlag":
            return False
        elif t == "ParameterGreaterThan":
            value = float(self.context.get_parameter(condition.parameter))
            return value > condition.value_float
        elif t == "ParameterGreaterOrEqual":
            value = float(self.context.get_parameter(condition.parameter))
            return value >= condition.value_float
        elif t == "ParameterLessThan":
            value = float(self.context.get_parameter(condition.parameter))
            return value < condition.value_float
        elif t == "ParameterLessOrEqual":
            value = float(self.context.get_parameter(condition.parameter))
            return value <= condition.value_float
        elif t == "TimeGreaterThan":
            return self.context.active_state_time > condition.value_float
        elif t == "TimeLessThan":
            return self.context.active_state_time < condition.value_float
        elif t == "EventOccurred":
            return False
        elif t == "BoolParameterExists":
            return False
        elif t == "BoolParameterEquals":
            value = bool(self.context.get_parameter(condition.parameter))
            return value == condition.value_bool
        else:
            assert False, "Unknown condition type: " + t

    def _evaluate_active_state(self):
        dt = self.context.delta_time
        transition_frame = None
        transition_progress = 0.0
        # blend all active transitions
        for t in self.active_transitions:
            next_transition_frame = t.update(self.context)
            if transition_frame is None:
                transition_frame = next_transition_frame
            else:
                transition_frame.blend(next_transition_frame, transition_progress)
            transition_progress = t.progress

        # remove finished transitions
        self.active_transitions = [t for t in self.active_transitions if t.progress < 1.0]

        # evaluate active state
        if self.active_animation_tree_player is not None:
            active_frame = self.active_animation_tree_player.update(dt)
        elif self.active_state_machine_player is not None:
            active_frame = self.active_state_machine_player.update(dt)
        else:
            active_frame = FrameBuffer(self.context.num_bones)

        # blend active state with transitions
        if transition_frame is None:
            return active_frame
        else:
            transition_frame.blend(active_frame, transition_progress)
            return transition_frame

    def _get_start_node(self):
        for n in self.state_machine.nodes:
            if n.bl_idname == SMNodeStart.bl_idname:
                return n
        return None
