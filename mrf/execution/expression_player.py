import mathutils
import numpy as np

from .frame_buffer import FrameBuffer
from .mathex import quaternion_multiply_single, quaternion_slerp_single
from ...cwxml.yed import Expression, ExpressionInstrBone


class ExpressionPlayer:
    def __init__(self, armature_obj, expression):
        assert isinstance(expression, Expression)

        self.expression = expression
        self.armature_obj = armature_obj
        self.num_bones = len(self.armature_obj.pose.bones)
        self.stack = np.empty((512, 4), dtype=np.float32)
        self.time = 0.0

        self.false_true = np.array([0, 0xFFFFFFFF], dtype=np.uint32)

        self.bone_matrices = np.empty((self.num_bones, 4, 4), dtype=np.float32)
        self.bone_id_to_index = {}
        for bone_index, pose_bone in enumerate(self.armature_obj.pose.bones):
            bone = pose_bone.bone
            self.bone_id_to_index[bone.bone_properties.tag] = bone_index

            mat = bone.matrix_local
            if bone.parent is not None:
                mat = bone.parent.matrix_local.inverted() @ mat
            self.bone_matrices[bone_index, :, :] = np.asarray(mat)

    def update(self, delta_time, frame):
        self.time += delta_time
        for stream in self.expression.streams:
            self._process_stream(delta_time, frame, stream)

    def _process_stream(self, delta_time, frame, stream):
        stack = self.stack
        stack_u32 = stack.view(dtype=np.uint32)
        stack_top = -1
        i = 0
        instrs = stream.instructions
        while i < len(instrs):
            instr = instrs[i]
            if instr.type == "Pop":
                stack_top -= 1
            elif instr.type == "Dup":
                stack_top += 1
                stack[stack_top] = stack[stack_top - 1]
            elif instr.type == "Push0":
                stack_top += 1
                stack[stack_top, :] = 0.0
            elif instr.type == "Push1":
                stack_top += 1
                stack[stack_top, :] = 1.0
            elif instr.type == "PushFloat":
                stack_top += 1
                stack[stack_top, :] = instr.value
            elif instr.type == "TrackGet":
                stack_top += 1
                self._track_get(instr, frame, out=stack[stack_top])
            elif instr.type == "TrackGetComp":
                stack_top += 1
                self._track_get(instr, frame, out=stack[stack_top])
                stack[stack_top, :] = stack[stack_top, instr.component_index]
            elif instr.type == "TrackGetOffset":
                assert False, "TODO: implement TrackGetOffset"
            elif instr.type == "TrackGetOffsetComp":
                assert False, "TODO: implement TrackGetOffsetComp"
            elif instr.type == "TrackGetBoneTransform":
                assert False, "TODO: implement TrackGetBoneTransform"
            elif instr.type == "PushVector":
                stack_top += 1
                stack[stack_top, :] = instr.value
            elif instr.type == "DefineSpring":
                pass  # springs are simulated after the whole animation tree is evaluated
            elif instr.type == "VectorAbs":
                np.fabs(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorNeg":
                np.negative(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorRcp":
                np.reciprocal(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorSqrt":
                np.sqrt(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorCos":
                np.cos(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorSin":
                np.sin(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorTan":
                np.tan(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorACos":
                np.arccos(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorASin":
                np.arcsin(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorATan":
                np.arctan(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorNeg3":
                np.negative(stack[stack_top, :3], out=stack[stack_top, :3])
            elif instr.type == "VectorSquare":
                stack[stack_top] *= stack[stack_top]
            elif instr.type == "VectorDeg2Rad":
                np.deg2rad(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorRad2Deg":
                np.rad2deg(stack[stack_top], out=stack[stack_top])
            elif instr.type == "VectorSaturate":
                np.clip(stack[stack_top], 0.0, 1.0, out=stack[stack_top])
            elif instr.type == "TrackValid":
                assert False, "TODO: implement TrackValid"
            elif instr.type == "FromEuler":
                assert False, "TODO: implement FromEuler"
            elif instr.type == "ToEuler":
                assert False, "TODO: implement ToEuler"
            elif instr.type == "TrackSet":
                v = stack[stack_top]
                stack_top -= 1

                bone_idx = self.bone_id_to_index[instr.bone_id]
                if instr.track == 2: # bone scale
                    frame.scale_data[bone_idx, :] = v[:3]
                else:
                    assert False, f"Unknown track: {instr.track}"
            elif instr.type == "TrackSetComp":
                assert False, "TODO: implement TrackSetComp"
            elif instr.type == "TrackSetOffset":
                assert False, "TODO: implement TrackSetOffset"
            elif instr.type == "TrackSetOffsetComp":
                assert False, "TODO: implement TrackSetOffsetComp"
            elif instr.type == "TrackSetBoneTransform":
                assert False, "TODO: implement TrackSetBoneTransform"
            elif instr.type == "Jump":
                i += instr.instruction_offset
                continue  # skip i += 1
            elif instr.type == "JumpIfTrue":
                # note: stack is not modified
                if stack[stack_top].any():
                    i += instr.instruction_offset
                    continue
            elif instr.type == "JumpIfFalse":
                if not stack[stack_top].any():
                    i += instr.instruction_offset
                    continue
            elif instr.type == "VectorAdd":
                stack_top -= 1
                stack[stack_top] += stack[stack_top + 1]
            elif instr.type == "VectorSub":
                stack_top -= 1
                stack[stack_top] -= stack[stack_top + 1]
            elif instr.type == "VectorMul":
                stack_top -= 1
                stack[stack_top] *= stack[stack_top + 1]
            elif instr.type == "VectorMin":
                stack_top -= 1
                np.fmin(stack[stack_top], stack[stack_top + 1], out=stack[stack_top])
            elif instr.type == "VectorMax":
                stack_top -= 1
                np.fmax(stack[stack_top], stack[stack_top + 1], out=stack[stack_top])
            elif instr.type == "QuatMul":
                stack_top -= 1
                quaternion_multiply_single(stack[stack_top], stack[stack_top + 1])
            elif instr.type == "VectorGreaterThan":
                stack_top -= 1
                np.choose(stack[stack_top] > stack[stack_top + 1], self.false_true, out=stack_u32[stack_top])
            elif instr.type == "VectorLessThan":
                stack_top -= 1
                np.choose(stack[stack_top] < stack[stack_top + 1], self.false_true, out=stack_u32[stack_top])
            elif instr.type == "VectorGreaterEqual":
                stack_top -= 1
                np.choose(stack[stack_top] >= stack[stack_top + 1], self.false_true, out=stack_u32[stack_top])
            elif instr.type == "VectorLessEqual":
                stack_top -= 1
                np.choose(stack[stack_top] <= stack[stack_top + 1], self.false_true, out=stack_u32[stack_top])
            elif instr.type == "VectorClamp":
                stack_top -= 2
                np.clip(stack[stack_top], stack[stack_top + 1], stack[stack_top + 2], out=stack[stack_top])
            elif instr.type == "VectorLerp":
                assert False, "TODO: implement VectorLerp"
            elif instr.type == "VectorMad":
                assert False, "TODO: implement VectorMad"
            elif instr.type == "QuatSlerp":
                stack_top -= 2
                quaternion_slerp_single(stack[stack_top], stack[stack_top + 1], stack[stack_top + 2, 0])
            elif instr.type == "ToVector":
                stack_top -= 2
                # stack[stack_top, 0] = stack[stack_top, 0]    # x (already there)
                stack[stack_top, 1] = stack[stack_top + 1, 0]  # y
                stack[stack_top, 2] = stack[stack_top + 2, 0]  # z
                # stack[stack_top, 3] = 0.0                    # w (unused, can be garbage)
            elif instr.type == "LookAt":
                assert False, "TODO: implement LookAt"
            elif instr.type == "PushTime":
                stack_top += 1
                stack[stack_top, :] = self.time
            elif instr.type == "VectorTransform":
                assert False, "TODO: implement VectorTransform"
            elif instr.type == "GetVariable":
                assert False, "TODO: implement GetVariable"
            elif instr.type == "SetVariable":
                assert False, "TODO: implement SetVariable"
            elif instr.type == "BlendVector":
                assert False, "TODO: implement BlendVector"
            elif instr.type == "BlendQuaternion":
                assert False, "TODO: implement BlendQuaternion"
            elif instr.type == "PushDeltaTime":
                stack_top += 1
                stack[stack_top, :] = delta_time
            elif instr.type == "VectorEqual":
                stack_top -= 1
                np.choose(stack[stack_top] == stack[stack_top + 1], self.false_true, out=stack_u32[stack_top])
            elif instr.type == "VectorNotEqual":
                stack_top -= 1
                np.choose(stack[stack_top] != stack[stack_top + 1], self.false_true, out=stack_u32[stack_top])
            else:
                assert False, f"Unknown instruction: {instr.type}"

            i += 1

    def _track_get(self, instr: ExpressionInstrBone, frame, out):
        # TODO: consider use_defaults
        # TODO: if track value is invalid (0xFFFFFFFF) should return default value
        bone_idx = self.bone_id_to_index[instr.bone_id]
        if instr.track == 0:  # bone position
            # convert to local space
            # TODO: avoid np.append since it allocates a new array every call
            out[:] = self.bone_matrices[bone_idx] @ np.append(frame.position_data[bone_idx], 1.0)
        elif instr.track == 1:  # bone rotation
            # convert to local space
            out[:] = np.asarray(mathutils.Matrix(self.bone_matrices[bone_idx]).to_quaternion())
            quaternion_multiply_single(out, frame.rotation_data[bone_idx])
        elif instr.track == 2:  # bone scale
            out[:3] = frame.scale_data[bone_idx]
        else:
            assert False, f"Unknown track: {instr.track}"

    def _track_get_offset(self, instr: ExpressionInstrBone, frame: FrameBuffer, out: np.ndarray):
        bone_idx = self.bone_id_to_index[instr.bone_id]
        if instr.track == 0:  # bone position
            out[:3] = frame.position_data[bone_idx]
        elif instr.track == 1:  # bone rotation
            out[:] = frame.rotation_data[bone_idx]  # TODO: convert to euler
        elif instr.track == 2:  # bone scale
            out[:3] = frame.scale_data[bone_idx]
        else:
            assert False, f"Unknown track: {instr.track}"
