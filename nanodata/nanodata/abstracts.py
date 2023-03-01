import os
import numpy as np
from typing import Iterable, Any, Iterator

from . import interfaces
from . import errors


class DataManager(
    interfaces.IDataManager[interfaces.TDataSet, interfaces.TDataSetType],
):
    def __init__(self, path: str):
        self._path = path
        self._data_sets: dict[str, interfaces.TDataSet] = {}
        self._file_types: list[interfaces.TDataSetType] = []

    def _add_data_set(self, data_set: interfaces.TDataSet) -> None:
        if data_set.name in self._data_sets:
            raise errors.DataSetExistsError(
                f"Data set with name '{data_set.name}' already exists."
            )
        self._data_sets[data_set.name] = data_set

    def _remove_data_set(self, name: str) -> None:
        if name in self._data_sets:
            del self._data_sets[name]
        else:
            raise errors.DataSetNotFoundError(f"Data set with name '{name}' not found.")

    def register_file_type(self, file_type: interfaces.TDataSetType) -> None:
        if file_type not in self._file_types:
            self._file_types.append(file_type)
        else:
            raise errors.DataSetTypeExistsError(
                f"Data set type '{file_type}' already exists."
            )

    def load(self) -> None:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Path '{self.path}' does not exist.")
        for directory in os.walk(self.path):
            file_names = directory[2]
            for file_name in file_names:
                file_path = os.path.join(directory[0], file_name)
                self.load_file(file_path)

    def load_file(self, file_path: str) -> None:
        file_name, _ = os.path.splitext(file_path)
        for file_type in self._file_types:
            if file_type.is_valid(file_path):
                data_set = file_type.create_data_set(file_name, file_path)
                data_set.load()
                self._add_data_set(data_set)
                break

    def load_data_set(self, name: str) -> None:
        if name in self._data_sets:
            self._data_sets[name].load()
        else:
            raise errors.DataSetNotFoundError(f"Data set with name '{name}' not found.")

    def apply_filter(self):
        # TODO IMPLEMENT
        # ? Passing entire data set object probably not efficient
        # ? Should get filter params and match those to instance vars of data set
        pass

    def clear(self) -> None:
        self._data_sets.clear()

    @property
    def values(self) -> Iterable[interfaces.TDataSet]:
        return self._data_sets.values()

    @property
    def items(self) -> Iterable[tuple[str, interfaces.TDataSet]]:
        return self._data_sets.items()  # type: ignore

    @property
    def keys(self) -> Iterable[str]:
        return self._data_sets.keys()

    @property
    def path(self) -> str:
        return self._path

    @property
    def data_sets(self) -> Iterable[interfaces.TDataSet]:
        return self._data_sets.values()

    def __getitem__(self, name: str) -> interfaces.TDataSet:
        if name in self._data_sets:
            return self._data_sets[name]
        else:
            raise errors.DataSetNotFoundError(f"Data set with name '{name}' not found.")

    def __len__(self) -> int:
        return len(self._data_sets)

    def __iter__(self) -> Iterator[interfaces.TDataSet]:
        return iter(self._data_sets.values())

    def __repr__(self) -> str:
        return f"{self.__name__}(path={self.path!r}, data_sets={len(self)!r}, file_types={self._file_types!r})"


class DataSet(interfaces.IDataSet):
    def __init__(self, name: str, path: str):
        self._name: str = name
        self._path: str = path
        self._active: bool = True

    def load(self) -> None:
        pass

    @staticmethod
    def _get_fraction(data: np.ndarray, percent: float) -> np.ndarray:
        """Returns a fraction of the data.

        Args:
            data (np.ndarray): The ndarray data to get the fraction from.
            percent (float): The percentage of the data to return.

        Returns:
            np.ndarray: The reduced data.
        """
        return data[:: int(100 / percent)]

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._path

    @property
    def active(self) -> bool:
        return self._active

    def activate(self):
        self._active = True

    def deactivate(self):
        self._active = False

    def __repr__(self) -> str:
        return f"DataSet(name={self.name!r}, path={self.path!r})"


class DataSetType(interfaces.IDataSetType):
    def __init__(
        self, name: str, extensions: list[str], data_type: type[interfaces.TDataSet]
    ):
        self._name: str = name
        self._extensions: list[str] = extensions
        self._data_type: type[interfaces.TDataSet] = data_type

    def create_data_set(self, name: str, path: str) -> interfaces.TDataSet:
        return self._data_type(name, path)

    def has_valid_extension(self, path: str) -> bool:
        _, file_extension = os.path.splitext(path)
        return file_extension in self._extensions

    def has_valid_header(self, path: str) -> bool:
        raise NotImplementedError()

    def is_valid(self, path: str) -> bool:
        return self.has_valid_extension(path) and self.has_valid_header(path)

    @property
    def extensions(self) -> Iterable[str]:
        return self._extensions

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"{self.__name__}(extensions={self.extensions!r})"


class Segment(interfaces.ISegment):
    def __init__(self, data: dict[str, Any]):
        self._data: dict[str, Any] = data

    @property
    def time(self) -> np.ndarray:
        """np.ndarray: Returns the time data of the data set."""
        return self._data.get("time", np.array([]))

    @time.setter
    def time(self, value: np.ndarray):
        self._data["time"] = value

    @property
    def force(self) -> np.ndarray:
        """np.ndarray: Returns the force data of the data set."""
        return self._data.get("force", np.array([]))

    @force.setter
    def force(self, value: np.ndarray):
        self._data["force"] = value

    @property
    def deflection(self) -> np.ndarray:
        """np.ndarray: Returns the deflection data of the data set."""
        return self._data.get("deflection", np.array([]))

    @deflection.setter
    def deflection(self, value: np.ndarray):
        self._data["deflection"] = value

    @property
    def z(self) -> np.ndarray:
        """np.ndarray: Returns the z data of the data set."""
        return self._data.get("z", np.array([]))

    @z.setter
    def z(self, value: np.ndarray):
        self._data["z"] = value

    @property
    def indentation(self) -> np.ndarray:
        """np.ndarray: Returns the indentation data of the data set."""
        return self._data.get("indentation", np.array([]))

    @indentation.setter
    def indentation(self, value: np.ndarray):
        self._data["indentation"] = value

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    def __getitem__(self, key: str) -> Any:
        return self._data.get(key, None)

    def __repr__(self) -> str:
        return f"Segment(data={self.data!r})"
