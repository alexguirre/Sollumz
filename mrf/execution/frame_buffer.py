import numpy as np


def quaternion_multiply(a, b):  # return in q1
    # https://github.com/blender/blender/blob/c89461a2bc844a459f76a7fb1808739d44ba378f/source/blender/blenlib/intern/math_rotation.c#L46
    t0 = a[:, 0] * b[:, 0] - a[:, 1] * b[:, 1] - a[:, 2] * b[:, 2] - a[:, 3] * b[:, 3]
    t1 = a[:, 0] * b[:, 1] + a[:, 1] * b[:, 0] + a[:, 2] * b[:, 3] - a[:, 3] * b[:, 2]
    t2 = a[:, 0] * b[:, 2] + a[:, 2] * b[:, 0] + a[:, 3] * b[:, 1] - a[:, 1] * b[:, 3]
    a[:, 3] = a[:, 0] * b[:, 3] + a[:, 3] * b[:, 0] + a[:, 1] * b[:, 2] - a[:, 2] * b[:, 1]
    a[:, 0] = t0
    a[:, 1] = t1
    a[:, 2] = t2


def quaternion_dot(a, b):  # return new array
    return a[:, 0] * b[:, 0] + a[:, 1] * b[:, 1] + a[:, 2] * b[:, 2] + a[:, 3] * b[:, 3]


def quaternion_slerp(a, b, t):  # return in q1
    # https://github.com/blender/blender/blob/c89461a2bc844a459f76a7fb1808739d44ba378f/source/blender/blenlib/intern/math_rotation.c#L876
    cosom = quaternion_dot(a, b)
    print("len(cosom) = %s   %s" % (len(cosom), cosom))

    neg_mask = cosom < 0.0
    cosom[neg_mask] = -cosom[neg_mask]
    a[neg_mask] = -a[neg_mask]

    # dot slerp
    w = np.zeros((len(cosom), 2), dtype=np.float32)
    in_range_mask = np.abs(cosom) < 0.99999
    not_in_range_mask = ~in_range_mask

    omega = np.arccos(cosom[in_range_mask])
    sinom = np.sin(omega)
    print("len(omega) = %s" % len(omega))
    print("len(sinom) = %s" % len(sinom))
    print("len(...) = %s" % len(np.sin((1.0 - t) * omega) / sinom))
    print("len(w[in_range_mask, 0]) = %s" % len(w[in_range_mask, 0]))
    w[in_range_mask, 0] = np.sin((1.0 - t) * omega) / sinom
    w[in_range_mask, 1] = np.sin(t * omega) / sinom

    # fallback to lerp
    w[not_in_range_mask, 0] = 1.0 - t
    w[not_in_range_mask, 1] = t

    t0 = w[:, 0] * a[:, 0] + w[:, 1] * b[:, 0]
    t1 = w[:, 0] * a[:, 1] + w[:, 1] * b[:, 1]
    t2 = w[:, 0] * a[:, 2] + w[:, 1] * b[:, 2]
    t3 = w[:, 0] * a[:, 3] + w[:, 1] * b[:, 3]
    a[:, 0] = t0
    a[:, 1] = t1
    a[:, 2] = t2
    a[:, 3] = t3

class FrameBuffer:
    def __init__(self, num_bones):
        self.num_bones = num_bones
        self.position_data = np.zeros((num_bones, 3), dtype=np.float32)
        self.rotation_data = np.tile([1.0, 0.0, 0.0, 0.0], (num_bones, 1))
        self.scale_data = np.ones((num_bones, 3), dtype=np.float32)

    def apply_to_armature_obj(self, armature_obj):
        armature_obj.pose.bones.foreach_set("location", self.position_data.ravel())
        armature_obj.pose.bones.foreach_set("rotation_quaternion", self.rotation_data.ravel())
        armature_obj.pose.bones.foreach_set("scale", self.scale_data.ravel())

        armature_obj.pose.bones[0].location.x += 0.0  # workaround to trigger an update, otherwise the bones remain unchanged in the viewport

    def copy(self):
        new_frame_buffer = FrameBuffer(self.num_bones)
        new_frame_buffer.position_data[:] = self.position_data
        new_frame_buffer.rotation_data[:] = self.rotation_data
        new_frame_buffer.scale_data[:] = self.scale_data
        return new_frame_buffer

    def make_identity(self):
        self.position_data.fill(0.0)
        self.rotation_data[:] = [1.0, 0.0, 0.0, 0.0]
        self.scale_data.fill(1.0)

    def combine(self, other):
        self.position_data += other.position_data
        quaternion_multiply(self.rotation_data, other.rotation_data)
        self.scale_data *= other.scale_data

    def add(self, other):
        self.position_data += other.position_data

    def multiply(self, other):
        quaternion_multiply(self.rotation_data, other.rotation_data)
        self.scale_data *= other.scale_data

    def blend(self, other, weight):
        self.position_data = self.position_data * (1.0 - weight) + other.position_data * weight
        quaternion_slerp(self.rotation_data, other.rotation_data, weight)
        self.scale_data = self.scale_data * (1.0 - weight) + other.scale_data * weight
