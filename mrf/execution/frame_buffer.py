import numpy as np


def quaternion_multiply(a, b):  # return in a
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


def quaternion_slerp(a, b, t):  # return in a
    # https://github.com/blender/blender/blob/c89461a2bc844a459f76a7fb1808739d44ba378f/source/blender/blenlib/intern/math_rotation.c#L876
    cosom = quaternion_dot(a, b)

    neg_mask = cosom < 0.0
    cosom[neg_mask] = -cosom[neg_mask]
    a[neg_mask] = -a[neg_mask]

    # dot slerp
    w = np.zeros((len(cosom), 2), dtype=np.float32)
    in_range_mask = np.abs(cosom) < 0.99999
    not_in_range_mask = ~in_range_mask

    omega = np.arccos(cosom[in_range_mask])
    sinom = np.sin(omega)
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
    def __init__(self, num_bones, buffer_to_copy=None):
        self.num_bones = num_bones
        # allocate buffer that can hold position, rotation and scale data
        if buffer_to_copy is None:
            self.buffer = np.empty(num_bones * 10, dtype=np.float32)  # 10 -> (x y z) + (w x y z) + (x y z)
        else:
            self.buffer = buffer_to_copy.copy()
        self.buffer_u32 = self.buffer.view(dtype=np.uint32)

        # buffer views for position, rotation and scale data
        position_end = num_bones * 3  # 3 -> (x y z)
        rotation_end = num_bones * 7  # 7 -> (x y z) + (w x y z)
        self.position_data = self.buffer[:position_end].reshape((num_bones, 3))
        self.rotation_data = self.buffer[position_end:rotation_end].reshape((num_bones, 4))
        self.scale_data = self.buffer[rotation_end:].reshape((num_bones, 3))
        self.position_data_u32 = self.position_data.view(dtype=np.uint32)
        self.rotation_data_u32 = self.rotation_data.view(dtype=np.uint32)
        self.scale_data_u32 = self.scale_data.view(dtype=np.uint32)

        # default to invalid if not making a copy
        if buffer_to_copy is None:
            self.make_invalid()

    def apply_to_armature_obj(self, armature_obj):
        armature_obj.pose.bones.foreach_set("location", self.position_data.ravel())
        armature_obj.pose.bones.foreach_set("rotation_quaternion", self.rotation_data.ravel())
        armature_obj.pose.bones.foreach_set("scale", self.scale_data.ravel())

        armature_obj.pose.bones[0].location.x += 0.0  # workaround to trigger an update, otherwise the bones remain unchanged in the viewport

    def copy(self):
        return FrameBuffer(self.num_bones, self.buffer)

    def make_identity(self):
        # note for quaternions 'fill(0.0) + [:,0] = 1.0' is faster than '[:] = [1.0, 0.0, 0.0, 0.0]'
        self.buffer[:self.num_bones * 7].fill(0.0)  # position and rotation to zero
        self.rotation_data[:, 0] = 1.0              # rotation to identity
        self.scale_data.fill(1.0)                   # scale to one

    def make_invalid(self):
        self.buffer_u32.fill(0xFFFFFFFF)

    # TODO: masking may be creating lots of intermediate allocations and slowing things down

    def combine(self, other):
        valid_mask = self.position_valid_mask(other)
        self.position_data[valid_mask] += other.position_data[valid_mask]

        valid_mask = self.rotation_valid_mask(other)
        r = self.rotation_data[valid_mask].reshape(-1, 4)
        quaternion_multiply(r, other.rotation_data[valid_mask].reshape(-1, 4))
        self.rotation_data[valid_mask] = r.flatten()

        valid_mask = self.scale_valid_mask(other)
        self.scale_data[valid_mask] *= other.scale_data[valid_mask]

    def add(self, other):
        valid_mask = self.position_valid_mask(other)
        self.position_data[valid_mask] += other.position_data[valid_mask]

    def multiply(self, other):
        valid_mask = self.rotation_valid_mask(other)
        r = self.rotation_data[valid_mask].reshape(-1, 4)
        quaternion_multiply(r, other.rotation_data[valid_mask].reshape(-1, 4))
        self.rotation_data[valid_mask] = r.flatten()

        valid_mask = self.scale_valid_mask(other)
        self.scale_data[valid_mask] *= other.scale_data[valid_mask]

    def blend(self, other, weight):
        valid_mask = self.position_valid_mask(other)
        self.position_data[valid_mask] += weight * (other.position_data[valid_mask] - self.position_data[valid_mask])

        valid_mask = self.rotation_valid_mask(other)
        r = self.rotation_data[valid_mask].reshape(-1, 4)
        quaternion_slerp(r, other.rotation_data[valid_mask].reshape(-1, 4), weight)
        self.rotation_data[valid_mask] = r.flatten()

        valid_mask = self.scale_valid_mask(other)
        self.scale_data[valid_mask] += weight * (other.scale_data[valid_mask] - self.scale_data[valid_mask])

    def merge(self, other):
        """
        Set invalid values of this frame to the values of the other frame.
        """
        invalid_mask = self.buffer_u32 == 0xFFFFFFFF
        self.buffer_u32[invalid_mask] = other.buffer_u32[invalid_mask]

    def position_valid_mask(self, other):
        return (self.position_data_u32 != 0xFFFFFFFF) & (other.position_data_u32 != 0xFFFFFFFF)

    def rotation_valid_mask(self, other):
        return (self.rotation_data_u32 != 0xFFFFFFFF) & (other.rotation_data_u32 != 0xFFFFFFFF)

    def scale_valid_mask(self, other):
        return (self.scale_data_u32 != 0xFFFFFFFF) & (other.scale_data_u32 != 0xFFFFFFFF)
