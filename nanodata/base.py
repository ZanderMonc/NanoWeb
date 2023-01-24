import os
from typing import Iterable, Optional
from abc import ABC, abstractmethod

from abstract import (
    AbstractDataManager,
    AbstractDataSet,
    AbstractDataSetType,
    AbstractSegment,
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

    def register_file_type(self, file_type: "DataSetType") -> None:
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
