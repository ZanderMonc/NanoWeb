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


##################################
#### Data Sets ###################
##################################


class ChiaroDataSet(NanoDataSet):
    def __init__(self, name: str, path: str):
        super().__init__(name, path)

    def _load_header(self, lines: list[str]) -> int:
        """Loads the header of the chiaro data set.

        Args:
            lines (list[str]): list of file lines

        Returns:
            int: Line number for the start of the body
        """
        reading_header: bool = True
        current_line: int = 0
        # TODO figure out where these are relevant
        targets = [
            "Time (s)",
            "Loading / unloading time (s)",
            "Calibration factor",
        ]

        float_targets: dict[str, str] = {
            "X-position (um)": "x_pos",
            "Y-position (um)": "y_pos",
            "Z-position (um)": "z_pos",
            "Z surface (um)": "z_surface",
            "Piezo position (nm) (Measured)": "piezo_pos",
            "k (N/m)": "cantilever_k",
            "Tip radius (um)": "tip_radius",
            "Calibration factor": "cantilever_lever",
            "Wavelength (nm)": "wavelength",
            "dX before scan (um)": "dx_before_scan",
            "Piezo position setpoint at start (nm)": "piezo_pos_setpoint",
            "P[max] (uN)": "max_force",
            "D[max] (nm)": "max_deflection",
            "D[final] (nm)": "final_deflection",
            "D[max-final] (nm)": "max_final_deflection",
            "Slope (N/m)": "slope",
            "E[eff] (Pa)": "effective_modulus",
            "SMDuration (s)": "sm_duration",
            "Depth (nm)": "depth",
        }

        string_targets: dict[str, str] = {
            "Auto find surface": "auto_find_surface",
            "Device:": "device",
            "Software version:": "version",
            "Control mode:": "mode",
            "Measurement:": "measurement",
            "Model:": "model",
            "Comment:": "comment",
        }

        while reading_header:
            line = lines[current_line]
            current_line += 1
            if line.startswith("Time (s)"):
                return current_line
            # TODO find cleaner way to do this specific if
            if line.startswith("E[v="):
                closed_square = line.find("]")
                self._header[line[: closed_square + 1]] = float(
                    line[closed_square + 7 :]
                )
                continue

            for target, name in float_targets.items():
                if line.startswith(target):
                    try:
                        self._header[name] = float(line[len(target) :].strip())
                    except ValueError:
                        # Value is not a float, e.g: "Not available in this mode". So don't add
                        # TODO create log message
                        pass
                    continue

            for target, name in string_targets.items():
                if line.startswith(target):
                    self._header[name] = line[len(target) :].strip()
                    continue

            if line.startswith("Profile:") or line.startswith(
                "Piezo Indentation Sweep Settings"
            ):
                protocol_points: list[tuple[float, float]] = []
                line = lines[current_line]
                # TODO add support for D/t[n] where n > 9 and clean up code
                while line.startswith("D[Z"):
                    t_index = line.find("t")
                    # d_name = line[:5].strip()
                    d_value = float(line[11 : t_index - 1].strip())
                    # t_name = line[t_index : t_index + 4].strip()
                    t_value = float(line[t_index + 8 :].strip())
                    # self._header[d_name] = d_value
                    # self._header[t_name] = t_value
                    protocol_points.append((d_value, t_value))

                    current_line += 1
                    line = lines[current_line]
                self._header["protocol"] = np.array(protocol_points)

        return 0

    def _load_body(self, lines: list[str], line_num: int = 0) -> None:
        # TODO this is copied from original, still needs adapting
        data = []
        for line in lines[line_num:]:
            line = line.strip().replace(",", ".").split("\t")
            # Time (s)	Load (uN)	Indentation (nm)	Cantilever (nm)	Piezo (nm)	Auxiliary
            # skip 2 = indentation and #5 auxiliary if present
            data.append(
                [
                    float(line[0]),  # time
                    float(line[1]),  # force
                    float(line[3]),  # z
                    float(line[4]),  # indentation
                    float(line[2]),  # deflection
                ]
            )

        data = np.array(data)

        time = data[:, 0]
        force = data[:, 1] * 1000.0
        deflection = data[:, 2]
        z = data[:, 3]
        indentation = data[:, 4]

        def create_segments_current():
            nodi = []
            nodi.append(0)
            mode = self._header.get("mode")

            if mode == "Indentation":
                signal = indentation
            elif mode == "Load":
                signal = force
            else:
                signal = z

            dy = np.abs(savgol_filter(signal, 101, 2, 2))
            for th in range(95, 100):
                threshold = np.percentile(dy, th)
                changes = find_peaks(dy, threshold)
                if len(changes[0]) < 10:
                    break
            for dtime in changes[0]:
                nodi.append(dtime)
            nodi.append(len(z) - 1)

            if len(nodi) > self.protocol.shape[0] + 2:
                # go safe mode
                nodi = []
                nodi.append(0)
                current_time = 0
                for seg_index in range(self.protocol.shape[0]):
                    current_time += self.protocol[seg_index, 1]
                    nodi.append(np.argmin((time - current_time) ** 2))

            for i in range(len(nodi) - 1):
                if (nodi[i + 1] - nodi[i]) < 2:
                    continue
                segment_z = z[nodi[i] : nodi[i + 1]]
                segment_force = force[nodi[i] : nodi[i + 1]]
                segment_time = time[nodi[i] : nodi[i + 1]]
                segment_indentation = indentation[nodi[i] : nodi[i + 1]]
                segment_deflection = deflection[nodi[i] : nodi[i + 1]]

                self.add_segment(
                    NanoSegment(
                        {
                            "z": segment_z,
                            "force": segment_force,
                            "time": segment_time,
                            "indentation": segment_indentation,
                            "deflection": segment_deflection,
                        }
                    )
                )

        def create_segments_2019(bias=30):
            actual_pos = 2
            nodi = []
            nodi.append(0)
            wait = 0
            for protocol_index in range(self.protocol.shape[0]):
                next_threshold = self.protocol[protocol_index, 0]
                next_time = self.protocol[protocol_index, 1]
                for j in range(actual_pos, len(z)):
                    if time[j] > wait + next_time:
                        if (
                            cross(
                                z[j],
                                z[j - 1],
                                next_threshold,
                                bias,
                            )
                            is True
                        ):
                            nodi.append(j)
                            wait = time[j]
                            break
                actual_pos = j
            nodi.append(len(z) - 1)
            for i in range(len(nodi) - 1):
                segment_z = z[nodi[i] : nodi[i + 1]]
                segment_force = force[nodi[i] : nodi[i + 1]]
                segment_time = time[nodi[i] : nodi[i + 1]]
                segment_indentation = indentation[nodi[i] : nodi[i + 1]]
                segment_deflection = deflection[nodi[i] : nodi[i + 1]]

                self.add_segment(
                    NanoSegment(
                        {
                            "z": segment_z,
                            "force": segment_force,
                            "time": segment_time,
                            "indentation": segment_indentation,
                            "deflection": segment_deflection,
                        }
                    )
                )

        # TODO figure out if Genova variant is necessary from experiment.py
        if self._header["version"] == "old":
            create_segments_2019()
        else:
            create_segments_current()


class NanoSurfDataSet(NanoDataSet):
    def __init__(self, name: str, path: str):
        super().__init__(name, path)

    def _load_header(self, lines: list[str]) -> int:
        # TODO implement header loading from experiment.py NanoSurf
        raise AbstractNotImplementedError()

    def _load_body(self, lines: list[str], line_num: int = 0) -> None:
        # TODO implement body loading from experiment.py NanoSurf
        raise AbstractNotImplementedError()

    def _create_segments(self) -> None:
        # TODO implement segment creation from experiment.py NanoSurf
        raise AbstractNotImplementedError()


# TODO Easytsv
# * experiment.py states there is no header, will need working out

# TODO Jpk
# * experiment.py shows that afmformats is used in this file and there is no load header, will need working out

# TODO JpkForceMap
# * experiment.py shows that afmformats is used in this file and there is no load header or body, will need working out

##################################
#### Data Set Types ##############
##################################


class ChiaroDataSetType(NanoDataSetType):
    def __init__(self):
        """Chiaro data set type. For Optics 11 format."""
        super().__init__("Chiaro", [".txt"], ChiaroDataSet)

    def is_valid(self, path: str) -> bool:
        with open(path) as file:
            signature = file.readline()

        if signature[0:5] == "Date\t":
            return True

        return False
