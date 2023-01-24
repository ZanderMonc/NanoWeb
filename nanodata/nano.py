import numpy as np

# TODO move these
def Gauss(x, x0, a0, s0) -> float:
    return a0 * np.exp(-(((x - x0) / s0) ** 2))


def Decay(x, A, s) -> float:
    return A * np.exp(-(x / s))


def GGauss(x, x1, x2, a1, a2, s1, s2) -> float:
    return a1 * np.exp(-(((x - x1) / s1) ** 2)) + a2 * np.exp(-(((x - x2) / s2) ** 2))


def cross(x1, x2, th, dth) -> bool:
    th1 = th + dth
    th2 = th - dth
    if np.sign(x1 - th1) != np.sign(x2 - th1):
        return True
    if np.sign(x1 - th2) != np.sign(x2 - th2):
        return True
    return False
