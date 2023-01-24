import os
import numpy as np
from typing import Iterable, Optional, Any
from abc import ABC, abstractmethod

from abstract import (
    AbstractDataManager,
    AbstractDataSet,
    AbstractDataSetType,
    AbstractSegment,
    TDataSet,
)

from errors import AbstractNotImplementedError

##################################
#### Data Managers ###############
##################################


class DataManager(AbstractDataManager, ABC):
    """Base class for managing data sets.

    Is effectively a dictionary of data sets which points to top level directory.

    Args:
        dir_path (str): Path to the directory containing the data sets.
    """

    def __init__(self, dir_path: str):
        super().__init__(dir_path)

    def add_data_set(self, data_set: "DataSet") -> None:
        """Adds a data set to the manager. Raises an error if a data set with the same name already exists."""
        if data_set.name in self._data_sets:
            raise ValueError(f"DataSet with name '{data_set.name}' already exists.")
        self._data_sets[data_set.name] = data_set

    def remove_data_set(self, name: str) -> None:
        """Removes the data set with the given name from the manager. Raises an error if it does not exist."""
        if name in self._data_sets:
            del self._data_sets[name]
        else:
            raise ValueError(f"DataSet with name '{name}' does not exist.")

    def get_data_set(self, name: str) -> Optional["DataSet"]:
        """Returns the data set with the given name. Returns None if it does not exist."""
        return self._data_sets.get(name)

    def register_file_type(self, file_type: "TDataSet") -> None:
        """Registers a file type with the manager."""
        self._file_types.append(file_type)

    def preload(self) -> None:
        """Preloads all data sets in the manager."""
        for directory in os.walk(self.path):
            for file_name in directory[2]:
                file_path = os.path.join(directory[0], file_name)
                file_name, file_extension = os.path.splitext(file_path)
                for file_type in self._file_types:
                    if file_extension in file_type.extensions:
                        if file_type.is_valid(file_path):
                            data_set = file_type.create_dataset(file_name, file_path)
                            # TODO move load to separate method
                            data_set.load()
                            self.add_data_set(data_set)
                            break

    def load_data_set(self, name: str) -> None:
        data_set = self.get_data_set(name)
        if data_set is None:
            raise ValueError(f"DataSet with name '{name}' does not exist.")
        data_set.load()

    def clear(self) -> None:
        """Clears the data sets in the manager."""
        self._data_sets.clear()

    @property
    def keys(self) -> Iterable[str]:
        """Iterable[str]: Returns the names of the data sets in the manager."""
        return self._data_sets.keys()

    @property
    def values(self) -> Iterable["DataSet"]:
        """Iterable[DataSet]: Returns the data sets in the manager."""
        return self._data_sets.values()

    @property
    def items(self) -> Iterable[tuple[str, "DataSet"]]:
        """Iterable[tuple[str, DataSet]]: Returns the names and data sets in the manager."""
        return self._data_sets.items()

    @property
    def path(self) -> str:
        """str: Returns the path to the directory containing the data sets."""
        return self._path

    def __len__(self) -> int:
        return len(self._data_sets)

    def __iter__(self) -> Iterable["DataSet"]:
        return iter(self.values)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(path={self._path}, data_sets={len(self)}"


##################################
#### Data Sets ###################
##################################


class DataSet(AbstractDataSet, ABC):
    """Base class for data sets.

    Args:
        name (str): Name of the data set.
        path (str): Path to the data set.
    """

    def __init__(self, name: str, path: str):
        super().__init__(name, path)

    def load(self) -> None:
        """Loads the data set."""
        raise AbstractNotImplementedError()

    @property
    def name(self) -> str:
        """str: Returns the name of the data set."""
        return self._name

    @property
    def path(self) -> str:
        """str: Returns the path to the data set."""
        return self._path

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self._name})"


class NanoDataSet(DataSet, ABC):
    """Abstract class for CellMechLab related data sets without AFMformats.

    Args:
        name (str): Name of the data set.
        path (str): Path to the data set.

    Attributes:
        _header (dict[str, float | str]): The header of the data set.
        _segments (list[Segment]): The segments of the data set.
        _active (bool): Whether the data set is active or not based on filters.
    """

    def __init__(self, name: str, path: str):
        super().__init__(name, path)
        self._header: dict[str, float | str] = {"version": "old"}
        # self._body: dict[str, Any] = {}
        self._segments: list[Segment] = []
        self._active: bool = True

    @abstractmethod
    def _load_header(self, lines: list[str]) -> int:
        raise AbstractNotImplementedError()

    @abstractmethod
    def _load_body(self, lines: list[str], line_num: int = 0) -> None:
        raise AbstractNotImplementedError()

    # @abstractmethod
    # def _create_segments(self) -> None:
    #     raise AbstractNotImplementedError()

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

    def _get_fraction(self, data: np.ndarray, percent: float) -> np.ndarray:
        """Returns a fraction of the data.

        Args:
            data (np.ndarray): The ndarray data to get the fraction from.
            percent (float): The percentage of the data to return.

        Returns:
            np.ndarray: The reduced data.
        """
        return data[:: int(100 / percent)]

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

    def activate(self) -> None:
        """Activates the data set."""
        self._active = True

    def deactivate(self) -> None:
        """Deactivates the data set."""
        self._active = False

    @property
    def header(self) -> dict[str, float | str]:
        """dict[str, float | str]: Returns the header of the data set."""
        return self._header

    @property
    def segments(self) -> list["Segment"]:
        """list[Segment]: Returns the segments of the data set."""
        return self._segments

    @property
    def protocol(self) -> np.ndarray:
        """np.ndarray: Returns the tip commands."""
        return self.header.get("protocol", np.empty((0, 2)))

    @property
    def time(self) -> np.ndarray:
        """np.ndarray: Returns the combined time data of all the segments."""
        return np.concatenate([segment.time for segment in self._segments])

    @property
    def force(self) -> np.ndarray:
        """np.ndarray: Returns the combined force data of all the segments"""
        return np.concatenate([segment.force for segment in self._segments])

    @property
    def deflection(self) -> np.ndarray:
        """np.ndarray: Returns the combined deflection data of all the segments"""
        return np.concatenate([segment.deflection for segment in self._segments])

    @property
    def z(self) -> np.ndarray:
        """np.ndarray: Returns the combined z data of all the segments"""
        return np.concatenate([segment.z for segment in self._segments])

    @property
    def indentation(self) -> np.ndarray:
        """np.ndarray: Returns the combined indentation data of all the segments"""
        return np.concatenate([segment.indentation for segment in self._segments])

    @property
    def tip_radius(self) -> float:
        """float: Returns the tip radius of the data set."""
        return self._header.get("tip_radius", 0.0)

    @property
    def cantilever_k(self) -> float:
        """float: Returns the cantilever spring constant of the data set."""
        return self._header.get("cantilever_k", 0.0)

    @property
    def active(self) -> bool:
        """bool: Returns whether the data set is active."""
        return self._active

    def __len__(self) -> int:
        return len(self.segments)

    def __iter__(self) -> Iterable["Segment"]:
        return iter(self.segments)


##################################
#### Data Set Types ##############
##################################


class DataSetType(AbstractDataSetType, ABC):
    """Base abstract class for all data set types.

    Args:
        name (str): Name of the data set type.
        extensions (list[str]): List of file extensions that are associated with this data set type.
        data_type (type[DataSetType]): Type class of the data set that is associated with this data set type.
    """

    def __init__(self, name: str, extensions: list[str], data_type: type[TDataSet]):
        self._name: str = name
        self._extensions: list[str] = extensions
        self._data_type = data_type

    def create_dataset(self, name: str, path: str) -> DataSet:
        """Create data set for self data type.

        Args:
            name (str): Data set name.
            path (str): Path to file.

        Returns:
            DataSet: Data set for self data type.
        """
        return self._data_type(name, path)

    @property
    def extensions(self) -> list[str]:
        """Get list of file extensions that are associated with this data set type."""
        return self._extensions

    @property
    def name(self) -> str:
        """Get name of the data set type."""
        return self._name


class NanoDataSetType(DataSetType, ABC):
    """Base abstract class for all data set types for CellMechLab.

    Args:
        name (str): Name of the data set type.
        extensions (list[str]): List of file extensions that are associated with this data set type.
        data_type (type[DataSetType]): Type class of the data set that is associated with this data set type.
    """

    def __init__(self, name: str, extensions: list[str], data_type: type[TDataSet]):
        super().__init__(name, extensions, data_type)


##################################
#### Segments ####################
##################################


class Segment(AbstractSegment, ABC):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)

    @abstractmethod
    def has_bilayer(self):
        raise AbstractNotImplementedError()

    @abstractmethod
    def set_data(self):
        raise AbstractNotImplementedError()

    @abstractmethod
    def get_n_odd(self):
        raise AbstractNotImplementedError()

    @abstractmethod
    def smooth(self):
        raise AbstractNotImplementedError()

    @abstractmethod
    def find_out_of_contact_region(self):
        raise AbstractNotImplementedError()

    @abstractmethod
    def find_contact_point(self):
        raise AbstractNotImplementedError()

    @abstractmethod
    def create_indentation(self):
        raise AbstractNotImplementedError()

    @abstractmethod
    def hertz(self):
        raise AbstractNotImplementedError()

    @abstractmethod
    def fit_hertz(self):
        raise AbstractNotImplementedError()

    def set_z(self, z: np.ndarray):
        self._data["z"] = z

    def set_f(self, f: np.ndarray):
        self._data["force"] = f

    @property
    def time(self) -> np.ndarray:
        """np.ndarray: Returns the time data of the data set."""
        return self._data.get("time", np.array([]))

    @property
    def force(self) -> np.ndarray:
        """np.ndarray: Returns the force data of the data set."""
        return self._data.get("force", np.array([]))

    @property
    def deflection(self) -> np.ndarray:
        """np.ndarray: Returns the deflection data of the data set."""
        return self._data.get("deflection", np.array([]))

    @property
    def z(self) -> np.ndarray:
        """np.ndarray: Returns the z data of the data set."""
        return self._data.get("z", np.array([]))

    @property
    def indentation(self) -> np.ndarray:
        """np.ndarray: Returns the indentation data of the data set."""
        return self._data.get("indentation", np.array([]))

    @property
    def data(self) -> dict[str, float | str]:
        """dict[str, float | str]: Returns the header of the data set."""
        return self._data
