import numpy as np

from typing import Any
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter, find_peaks, medfilt

from base import DataManager, NanoDataSet, NanoDataSetType, Segment
from errors import AbstractNotImplementedError

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


##################################
#### Data Managers ###############
##################################


class NanoDataManager(DataManager):
    """Class for managing data sets.

    Used for CellMechLab related data sets.
    All files types should be registered in the __init__.

    Args:
        dir_path (str): Path to the directory containing the data sets.
    """

    def __init__(self, dir_path: str):
        super().__init__(dir_path)
        ##################################
        #### Register File Types Here ####
        ##################################
        self.register_file_type(ChiaroDataSetType())

        # ! Below comments are placeholders for DataSetType names, subject to change
        # self.register_file_type(NanoSurfDataSetType())
        # self.register_file_type(EasyTsvDataSetType())
        # self.register_file_type(JpkDataSetType())
        # self.register_file_type(JpkForceMapDataSetType())

    def apply_filter(self):
        pass
