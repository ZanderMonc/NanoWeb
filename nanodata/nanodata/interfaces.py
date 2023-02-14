import abc

from typing import Iterable, TypeVar, Generic, Any

class IDataManager(abc.ABC, Generic[TDataSet, TDataSetType]):
    @abc.abstractmethod
    def _add_data_set(self, data_set: TDataSet) -> None:
        pass

    @abc.abstractmethod
    def _remove_data_set(self, name: str) -> None:
        pass

    @abc.abstractmethod
    def register_file_type(self, file_type: TDataSetType) -> None:
        pass

    @abc.abstractmethod
    def load(self) -> None:
        pass

    @abc.abstractmethod
    def load_data_set(self, name: str) -> None:
        pass

    @abc.abstractmethod
    def apply_filter(self):
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        pass

    @property
    @abc.abstractmethod
    def values(self) -> Iterable[TDataSet]:
        pass

    @property
    @abc.abstractmethod
    def items(self) -> Iterable[tuple[str, TDataSet]]:
        pass

    @property
    @abc.abstractmethod
    def keys(self) -> Iterable[str]:
        pass

    @property
    @abc.abstractmethod
    def path(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def datasets(self) -> Iterable[TDataSet]:
        pass

    @abc.abstractmethod
    def __getitem__(self, name: str) -> TDataSet:
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    @abc.abstractmethod
    def __iter__(self) -> Iterable[TDataSet]:
        pass

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass

class IDataSet(abc.ABC):
    @abc.abstractmethod
    def load(self) -> None:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def path(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def active(self) -> bool:
        pass

    @abc.abstractmethod
    def activate(self) -> None:
        pass

    @abc.abstractmethod
    def deactivate(self) -> None:
        pass

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass