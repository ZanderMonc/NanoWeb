import abc
import numpy as np

from typing import Iterable, TypeVar, Generic, Any

TDataSet = TypeVar("TDataSet", bound="IDataSet")
TDataSetType = TypeVar("TDataSetType", bound="IDataSetType")
TSegment = TypeVar("TSegment", bound="ISegment")


class Singleton(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractSingleton(Singleton, abc.ABCMeta):
    ...


class IDataManager(
    abc.ABC, Generic[TDataSet, TDataSetType], metaclass=AbstractSingleton
):
    @abc.abstractmethod
    def _add_data_set(self, data_set: TDataSet) -> None:
        ...

    @abc.abstractmethod
    def _remove_data_set(self, name: str) -> None:
        ...

    @abc.abstractmethod
    def register_file_type(self, file_type: TDataSetType) -> None:
        ...

    @abc.abstractmethod
    def load(self) -> None:
        ...

    @abc.abstractmethod
    def load_data_set(self, name: str) -> None:
        ...

    @abc.abstractmethod
    def clear(self) -> None:
        ...

    @property
    @abc.abstractmethod
    def values(self) -> Iterable[TDataSet]:
        ...

    @property
    @abc.abstractmethod
    def items(self) -> Iterable[tuple[str, TDataSet]]:
        ...

    @property
    @abc.abstractmethod
    def keys(self) -> Iterable[str]:
        ...

    @property
    @abc.abstractmethod
    def path(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def data_sets(self) -> Iterable[TDataSet]:
        ...

    @abc.abstractmethod
    def __getitem__(self, name: str) -> TDataSet:
        ...

    @abc.abstractmethod
    def __len__(self) -> int:
        ...

    @abc.abstractmethod
    def __iter__(self) -> Iterable[TDataSet]:
        ...

    @abc.abstractmethod
    def __repr__(self) -> str:
        ...


class IDataSet(abc.ABC):
    @abc.abstractmethod
    def load(self) -> None:
        ...

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def path(self) -> str:
        ...

    @abc.abstractmethod
    def __repr__(self) -> str:
        ...


class IDataSetType(abc.ABC):
    @abc.abstractmethod
    def is_valid(self, path: str) -> bool:
        ...

    @abc.abstractmethod
    def create_data_set(self, name: str, path: str) -> TDataSet:
        ...

    @abc.abstractmethod
    def has_valid_extension(self, path: str) -> bool:
        ...

    @abc.abstractmethod
    def has_valid_header(self, path: str) -> bool:
        ...

    @property
    @abc.abstractmethod
    def extensions(self) -> Iterable[str]:
        ...

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...


class ISegment(abc.ABC):
    @property
    @abc.abstractmethod
    def time(self) -> np.ndarray:
        ...

    @time.setter
    @abc.abstractmethod
    def time(self, value: np.ndarray):
        ...

    @property
    @abc.abstractmethod
    def force(self) -> np.ndarray:
        ...

    @force.setter
    @abc.abstractmethod
    def force(self, value: np.ndarray):
        ...

    @property
    @abc.abstractmethod
    def deflection(self) -> np.ndarray:
        ...

    @deflection.setter
    @abc.abstractmethod
    def deflection(self, value: np.ndarray):
        ...

    @property
    @abc.abstractmethod
    def z(self) -> np.ndarray:
        ...

    @z.setter
    @abc.abstractmethod
    def z(self, value: np.ndarray):
        ...

    @property
    @abc.abstractmethod
    def indentation(self) -> np.ndarray:
        ...

    @indentation.setter
    @abc.abstractmethod
    def indentation(self, value: np.ndarray):
        ...

    @property
    @abc.abstractmethod
    def data(self) -> dict[str, Any]:
        ...

    @abc.abstractmethod
    def __repr__(self) -> str:
        ...
