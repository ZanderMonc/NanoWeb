from abc import ABC, abstractmethod
from typing import Iterable, Optional, TypeVar

from errors import AbstractNotImplementedError

DataSetType = TypeVar("DataSetType", bound="AbstractDataSet")


class AbstractDataManager(ABC):
    """Abstract class for managing data sets.

    Is effectively a dictionary of data sets which points to top level directory.

    Args:
        dir_path (str): Path to the directory containing the data sets.
    """

    def __init__(self, dir_path: str):
        self._path: str = dir_path
        self._data_sets: dict[str, "AbstractDataSet"] = {}
        self._file_types: list["DataSetType"] = []

    @abstractmethod
    def add_data_set(self) -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def remove_data_set(self, name: str) -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def get_data_set(self, name: str) -> Optional["AbstractDataSet"]:
        raise AbstractNotImplementedError()

    @abstractmethod
    def register_file_type(self, file_type: "DataSetType") -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def preload(self) -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def load_data_set(self, name: str) -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def clear(self) -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def keys(self) -> Iterable[str]:
        raise AbstractNotImplementedError()

    @abstractmethod
    def values(self) -> Iterable["AbstractDataSet"]:
        raise AbstractNotImplementedError()

    @abstractmethod
    def items(self) -> Iterable[tuple[str, "AbstractDataSet"]]:
        raise AbstractNotImplementedError()

    @abstractmethod
    def path(self) -> str:
        raise AbstractNotImplementedError()


class AbstractDataSet(ABC):
    """Abstract class for data sets.

    Args:
        name (str): Name of the data set.
        path (str): Path to the data set.
    """

    def __init__(self, name: str, path: str):
        self._name: str = name
        self._path: str = path

    @abstractmethod
    def load(self) -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def name(self) -> str:
        raise AbstractNotImplementedError()

    @abstractmethod
    def path(self) -> str:
        raise AbstractNotImplementedError()


class AbstractDataSetType(ABC):
    """Base abstract class for all data set types.

    Args:
        name (str): Name of the data set type.
        extensions (list[str]): List of file extensions that are associated with this data set type.
        data_type (type[DataSetType]): Type class of the data set that is associated with this data set type.
    """

    def __init__(self, name: str, extensions: list[str], data_type: type[DataSetType]):
        self._name: str = name
        self._extensions: list[str] = extensions
        self._data_type = data_type

    @abstractmethod
    def is_valid(self, path: str) -> bool:
        """Check if file is valid for self data type.

        Args:
            path (str): Path to file.

        Raises:
            AbstractNotImplementedError: This method is abstract and needs to be implemented.

        Returns:
            bool: True if file is valid for self data type.
        """
        raise AbstractNotImplementedError()

    @abstractmethod
    def create_dataset(self) -> AbstractDataSet:
        """Create data set for self data type.

        Returns:
            DataSet: Data set for self data type.
        """
        raise AbstractNotImplementedError()

    @abstractmethod
    def extensions(self) -> list[str]:
        """Get list of file extensions that are associated with this data set type."""
        raise AbstractNotImplementedError()

    @abstractmethod
    def name(self) -> str:
        """Get name of the data set type."""
        raise AbstractNotImplementedError()


class AbstractSegment(ABC):
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

    @abstractmethod
    def set_z(self) -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def set_f(self) -> None:
        raise AbstractNotImplementedError()

    @abstractmethod
    def time(self):
        """Returns the time data of the data set."""
        raise AbstractNotImplementedError()

    @abstractmethod
    def force(self):
        """Returns the force data of the data set."""
        raise AbstractNotImplementedError()

    @abstractmethod
    def deflection(self):
        """Returns the deflection data of the data set."""
        raise AbstractNotImplementedError()

    @abstractmethod
    def z(self):
        """Returns the z data of the data set."""
        raise AbstractNotImplementedError()

    @abstractmethod
    def indentation(self):
        """Returns the indentation data of the data set."""
        raise AbstractNotImplementedError()

    @abstractmethod
    def data(self):
        """Returns the header of the data set."""
        raise AbstractNotImplementedError()
