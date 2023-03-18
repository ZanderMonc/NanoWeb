import numpy as np
import os

from typing import Any, Iterator
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter, find_peaks, medfilt

from . import abstracts


# TODO move these
def Gauss(x, x0, a0, s0) -> float:
    return a0 * np.exp(-(((x - x0) / s0) ** 2))


def Decay(x, A, s) -> float:
    return A * np.exp(-(x / s))


def GGauss(x, x1, x2, a1, a2, s1, s2) -> float:
    return a1 * np.exp(-(((x - x1) / s1) ** 2)) + a2 * np.exp(-(((x - x2) / s2) ** 2))


def can_be_crossed(x1, x2, th, dth) -> bool:
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


class ChiaroDataManager(abstracts.DataManager["ChiaroDataSet", "ChiaroDataSetType"]):
    """Class for managing chiaro/optics 11 data sets.

    All files types should be registered in the __init__.

    Args:
        dir_path (str): Path to the directory containing the data sets.
    """

    def __init__(self, dir_path: str):
        super().__init__(dir_path)
        self.register_file_type(ChiaroDataSetType())


##################################
#### Data Sets ###################
##################################


class ChiaroDataSet(abstracts.DataSet):
    def __init__(self, name: str, path: str):
        super().__init__(name, path)
        self._header: dict[str, float | str] = {"version": "old"}

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
                    line[closed_square + 7:]
                )
                continue

            for target, name in float_targets.items():
                if line.startswith(target):
                    try:
                        self._header[name] = float(line[len(target):].strip())
                    except ValueError:
                        # Value is not a float, e.g: "Not available in this mode". So don't add
                        # TODO create log message
                        pass
                    continue

            for target, name in string_targets.items():
                if line.startswith(target):
                    self._header[name] = line[len(target):].strip()
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
                    d_value = float(line[11: t_index - 1].strip())
                    # t_name = line[t_index : t_index + 4].strip()
                    t_value = float(line[t_index + 8:].strip())
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
                segment_z = z[nodi[i]: nodi[i + 1]]
                segment_force = force[nodi[i]: nodi[i + 1]]
                segment_time = time[nodi[i]: nodi[i + 1]]
                segment_indentation = indentation[nodi[i]: nodi[i + 1]]
                segment_deflection = deflection[nodi[i]: nodi[i + 1]]

                self.add_segment(
                    Segment(
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
                        if can_be_crossed(
                                z[j],
                                z[j - 1],
                                next_threshold,
                                bias,
                        ):
                            nodi.append(j)
                            wait = time[j]
                            break
                actual_pos = j
            nodi.append(len(z) - 1)
            for i in range(len(nodi) - 1):
                segment_z = z[nodi[i]: nodi[i + 1]]
                segment_force = force[nodi[i]: nodi[i + 1]]
                segment_time = time[nodi[i]: nodi[i + 1]]
                segment_indentation = indentation[nodi[i]: nodi[i + 1]]
                segment_deflection = deflection[nodi[i]: nodi[i + 1]]

                self.add_segment(
                    Segment(
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

    def load(self) -> None:
        # TODO check file extension
        lines: list[str]
        line_num: int

        if not os.path.exists(self._path):
            raise FileNotFoundError(f"File '{self._path}' does not exist.")
        with open(self.path, "r") as file:
            lines = file.readlines()
            lines = [
                line.strip() for line in lines if line.strip()
            ]  # remove empty lines

        # TODO verify that empty files actually have 0 lines
        if len(lines) == 0:
            raise ValueError(f"File '{self._path}' is empty.")

        line_num = self._load_header(lines)
        self._load_body(lines, line_num)
        # self._create_segments()

    def get_time_fraction(self, percent: float) -> np.ndarray:
        """Returns a fraction of the time data."""
        return self._get_fraction(self.time, percent)

    def get_force_fraction(self, percent: float) -> np.ndarray:
        """Returns a fraction of the force data."""
        return self._get_fraction(self.force, percent)

    def get_deflection_fraction(self, percent: float) -> np.ndarray:
        """Returns a fraction of the deflection data."""
        return self._get_fraction(self.deflection, percent)

    def get_z_fraction(self, percent: float) -> np.ndarray:
        """Returns a fraction of the z data."""
        return self._get_fraction(self.z, percent)

    def get_indentation_fraction(self, percent: float) -> np.ndarray:
        """Returns a fraction of the indentation data."""
        return self._get_fraction(self.indentation, percent)

    def add_segment(self, segment: "Segment") -> None:
        """Adds a segment to the data set.

        Args:
            segment (Segment): The segment to add.
        """
        if segment not in self._segments:
            self._segments.append(segment)
        else:
            raise ValueError("Segment already exists.")

    @property
    def header(self) -> dict[str, float | str]:
        """dict[str, float | str]: Returns the header of the data set."""
        return self._header

    @property
    def protocol(self) -> np.ndarray:
        """np.ndarray: Returns the tip commands."""
        return self.header.get("protocol", np.empty((0, 2)))

    @property
    def tip_radius(self) -> float:
        """float: Returns the tip radius of the data set."""
        return self._header.get("tip_radius", 0.0)

    @property
    def cantilever_k(self) -> float:
        """float: Returns the cantilever spring constant of the data set."""
        return self._header.get("cantilever_k", 0.0)

    def __len__(self) -> int:
        return len(self.segments)

    def __iter__(self) -> Iterator["Segment"]:
        return iter(self.segments)


class NanoSurfDataSet(abstracts.DataSet):
    def __init__(self, name: str, path: str):
        super().__init__(name, path)

    def _load_header(self, lines: list[str]) -> int:
        # TODO implement header loading from experiment.py NanoSurf
        pass

    def _load_body(self, lines: list[str], line_num: int = 0) -> None:
        # TODO implement body loading from experiment.py NanoSurf
        pass

    def _create_segments(self) -> None:
        # TODO implement segment creation from experiment.py NanoSurf
        pass


# TODO Easytsv
# * experiment.py states there is no header, will need working out

# TODO Jpk
# * experiment.py shows that afmformats is used in this file and there is no load header, will need working out

# TODO JpkForceMap
# * experiment.py shows that afmformats is used in this file and there is no load header or body, will need working out

##################################
#### Data Set Types ##############
##################################


class ChiaroDataSetType(abstracts.DataSetType):
    def __init__(self):
        """Chiaro data set type. For Optics 11 format."""
        super().__init__("Chiaro", [".txt"], ChiaroDataSet)

    def has_valid_header(self, path: str) -> bool:
        with open(path) as file:
            signature = file.readline()

        if signature[0:5] == "Date\t":
            return True

        return False


class NanoSurfDataSetType(abstracts.DataSetType):
    def __init__(self):
        super().__init__("NanoSurf", [".txt"], NanoSurfDataSet)

    def has_valid_header(self, path: str) -> bool:
        with open(path) as file:
            signature = file.readline()

        if signature[0:9] == "#Filename":
            return True

        return False


# TODO Easytsv DataSetType
# * experiment.py contains check which can be used

# TODO Jpk DataSetType
# * experiment.py shows that there is no check function, will need working out

# TODO JpkForceMap DataSetType
# * experiment.py shows that there is no check function, will need working out

##################################
#### Segments ####################
##################################


class Segment(abstracts.Segment):
    def __init__(self, data: dict[str, Any]):
        # TODO organise instance variables
        super().__init__(data)
        self._i_contact: int = 0
        self._out_contact: int = 0
        # self._parent = None
        self._mode_feedback = None
        self._mode_set_point = None
        self._mode_trigger = None
        self._mode_threshold = None
        self._poisson = 0.5
        self._young = None
        self._young_i_threshold = None
        self._touch = None
        self._h_indentation = None
        self._indentation = None
        self._h_touch = None
        self._h_pressure = None
        self._elastography = None
        self._filterLength = 1 / 30
        self._contactLength = 1 / 20

        # TODO change/move this calculation
        beg = int(len(self.z) / 3)
        end = int(2 * len(self.z) / 3)
        # ? for future reference maybe worth adding a fit ?
        self._speed = (self.z[end] - self.z[beg]) / (self.time[end] - self.time[beg])

    def has_bilayer(self):
        # TODO
        if self._elastography is not None and self._elastography.has_bilayer():
            return True
        return False

    def get_n_odd(self, fraction, total=None):
        # TODO not sure what purpose of this is
        if total is None:
            total = len(self.z)
        N = int(total * fraction)
        if N % 2 == 0:
            N += 1
        return N

    def smooth(self, method="sg"):
        # TODO
        N = self.get_n_odd(self._filterLength)
        if method == "sg":
            try:
                y = savgol_filter(self.force, N, 6, 0)
                self.force = y
            except:
                method = "basic"
        if method == "basic":
            self.force = medfilt(self.f, N)

    # Spots the segments where sample arm is not touching the sample
    # We were told this works as it is (partially) and that it is rather complicated (we don't have to fix this)
    # Dependencies : numpy, scipy (curve_fit)
    def find_out_of_contact_region(self, weight=20.0, refine=False):
        # TODO
        yy, xx = np.histogram(self.force, bins="auto")
        xx = (xx[1:] + xx[:-1]) / 2.0
        try:
            func = Gauss
            out = curve_fit(Gauss, xx, yy, p0=[xx[np.argmax(yy)], np.max(yy), 1.0])
            threshold = out[0][1] / weight
        except RuntimeError:
            try:
                func = Decay
                out = curve_fit(Decay, xx, yy, p0=[np.max(yy), 1.0])
                threshold = out[0][0] / weight
            except RuntimeError:
                return
        fit = func(xx, *out[0])
        if refine and len(out[0]) == 3:
            # try to refine
            x0, a0, s0 = out[0]
            try:
                out2 = curve_fit(GGauss, xx, yy, p0=[x0, x0 + s0, a0, a0 / 5.0, s0, s0])
                threshold = out2[0][2] / weight
            except RuntimeError:
                pass
        jend = 0
        for i in range(len(xx) - 1, 0, -1):
            if fit[i] < threshold and fit[i - 1] > threshold:
                jend = i
                break
        xcontact = np.max(self.z[self.f < xx[jend]])
        self.outContact = np.argmin((self.z - xcontact) ** 2)

    # Spot the segment where the sample arm is in contact with the sample.
    # Same as find_out_of_contact_region, part of the more complicated processes
    # Dependencies = numpy
    def find_contact_point(self):
        # TODO
        if self.outContact == 0:
            return
        pcoe = np.polyfit(self.z[: self.outContact], self.force[: self.outContact], 1)
        ypoly = np.polyval(pcoe, self.z)
        if self.f[self.outContact] < ypoly[self.outContact]:
            self.iContact = self.outContact
        else:
            for i in range(self.outContact, 0, -1):
                if self.f[i] < ypoly[i]:
                    self.iContact = i
                    break
        return True

    # Simulates the effect of an indentation of the sample, sets variables accordingly
    # Dependencies : numpy
    def create_indentation(self):
        # TODO
        if self.iContact == 0:
            return
        offsetY = np.average(self.force[: self.iContact])
        offsetX = self.z[self.iContact]
        Yf = self.f[self.iContact:] - offsetY
        Xf = self.z[self.iContact:] - offsetX
        self.indentation = Xf - Yf / self.parent.cantilever_k
        self.touch = Yf

    # Math - physics formula code
    # Port as it is
    # NB E should be in nN/nm^2 = 10^9 N/m^2 -> internal units for E is GPa
    def hertz(self, x, E=None):
        # TODO
        if E is None:
            E = self.young
        x = np.abs(x)
        # Eeff = E*1.0e9 #to convert E in GPa to keep consistency with the units nm and nN
        y = (
                (4.0 / 3.0)
                * (E / (1 - self.poisson ** 2))
                * np.sqrt(self.parent.tip_radius * x ** 3)
        )
        return y  # y will be in nN

    # Again, math code.
    # Port as it is
    # Dependencies = numpy, scipy (curve_fit)
    def fit_hertz(
            self, seed=1000.0 / 1e9, threshold=None, threshold_type="indentation"
    ):
        # TODO
        self.young = None
        if self.indentation is None:
            return
        x = self.indentation
        y = self.touch
        if threshold is not None:
            imax = len(x)
            if threshold_type == "indentation":
                if threshold > np.max(x):
                    return False
                imax = np.argmin((x - threshold) ** 2)
            else:
                if threshold > np.max(y) or threshold < np.min(y):
                    return False
                imax = np.argmin((y - threshold) ** 2)
            if imax > 10:
                x = x[:imax]
                y = y[:imax]
                self.youngIThreshold = imax
            else:
                return False
        seeds = [seed]
        # NB the curve is forced to have F=0 at indentation 0
        try:
            popt, pcov = curve_fit(self.hertz, x, y, p0=seeds, maxfev=10000)
            self.young = popt[0]
            self.H_indentation = x
            self.H_touch = y
            area = np.pi * self.parent.tip_radius * x
            self.H_pressure = y / area
            return self.young * 1e9

        except RuntimeError:
            return False

    @property
    def speed(self) -> int | float:
        return self._speed

#         _      _      _       _       _       _
#      __(.)< __(.)> __(.)=   >(.)__  >(.)__  >(.)__
#      \___)  \___)  \___)     (___/   (___/   (___/
