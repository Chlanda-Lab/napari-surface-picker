import numpy as np

def vec2euler(vec: np.ndarray, random_rot: bool=True) -> np.ndarray:
    """Vector is [Z, Y, X] of shape (3,) or (N, 3). The vectors have to be normalized.
    Returns array of shape (N, 3) with [rot, tilt, psi] in radians."""
    vec = vec.reshape((-1, 3))
    out = np.empty_like(vec, dtype=float)
    # psi: rotation around global Z axis
    np.arctan2(vec[:, 1], -vec[:, 2], out=out[:, 2])
    # tilt: rotation around new Y axis
    np.arccos(vec[:, 0], out=out[:, 1])
    # rot: rotation around new Z axis (random)
    if random_rot:
        out[:, 0] = np.random.rand(len(out)) * 2 * np.pi - np.pi
    else:
        out[:, 0] = 0
    return out
