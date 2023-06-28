import numpy as np


def quaternion_multiply(a, b):
    """
    Multiply two arrays of quaternions with shape (n, 4).
    Results are stored in-place in `a`.
    """
    # https://github.com/blender/blender/blob/c89461a2bc844a459f76a7fb1808739d44ba378f/source/blender/blenlib/intern/math_rotation.c#L46
    t0 = a[:, 0] * b[:, 0] - a[:, 1] * b[:, 1] - a[:, 2] * b[:, 2] - a[:, 3] * b[:, 3]
    t1 = a[:, 0] * b[:, 1] + a[:, 1] * b[:, 0] + a[:, 2] * b[:, 3] - a[:, 3] * b[:, 2]
    t2 = a[:, 0] * b[:, 2] + a[:, 2] * b[:, 0] + a[:, 3] * b[:, 1] - a[:, 1] * b[:, 3]
    a[:, 3] = a[:, 0] * b[:, 3] + a[:, 3] * b[:, 0] + a[:, 1] * b[:, 2] - a[:, 2] * b[:, 1]
    a[:, 0] = t0
    a[:, 1] = t1
    a[:, 2] = t2


def quaternion_multiply_single(a, b):
    """
    Multiply two quaternions.
    Results are stored in-place in `a`.
    """
    quaternion_multiply(a[np.newaxis], b[np.newaxis])


def quaternion_dot(a, b):
    """
    Calculate dot product of two arrays of quaternions with shape (n, 4).
    Results returned in a new array of length n
    """
    return a[:, 0] * b[:, 0] + a[:, 1] * b[:, 1] + a[:, 2] * b[:, 2] + a[:, 3] * b[:, 3]


def quaternion_slerp(a, b, t):
    """
    Slerp between two arrays of quaternions with shape (n, 4), from `a` to `b`.
    Results are stored in-place in `a`.
    """
    # https://github.com/blender/blender/blob/c89461a2bc844a459f76a7fb1808739d44ba378f/source/blender/blenlib/intern/math_rotation.c#L876
    cosom = quaternion_dot(a, b)

    neg_mask = cosom < 0.0
    cosom[neg_mask] = -cosom[neg_mask]
    a[neg_mask] = -a[neg_mask]

    # dot slerp
    w = np.empty((len(cosom), 2), dtype=np.float32)
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
    a[:, 3] = w[:, 0] * a[:, 3] + w[:, 1] * b[:, 3]
    a[:, 0] = t0
    a[:, 1] = t1
    a[:, 2] = t2


def quaternion_slerp_single(a, b, t):
    """
    Slerp between two quaternions.
    Results are stored in-place in `a`.
    """
    quaternion_slerp(a[np.newaxis], b[np.newaxis], t)
