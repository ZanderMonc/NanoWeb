from abc import ABC, abstractmethod, abstractproperty
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

    @abstractproperty
    def keys(self) -> Iterable[str]:
        raise AbstractNotImplementedError()

    @abstractproperty
    def values(self) -> Iterable["AbstractDataSet"]:
        raise AbstractNotImplementedError()

    @abstractproperty
    def items(self) -> Iterable[tuple[str, "AbstractDataSet"]]:
        raise AbstractNotImplementedError()

    @abstractproperty
    def path(self) -> str:
        raise AbstractNotImplementedError()
