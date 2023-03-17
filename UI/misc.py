from enum import StrEnum
import dataclasses
from typing import Any


class UISingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(UISingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataSetVars(StrEnum):
    TIME = "time"
    FORCE = "force"
    DEFLECTION = "deflection"
    Z = "z"
    INDENTATION = "indentation"


@dataclasses.dataclass
class UserFilterParameter:
    name: str
    data_type: type
    default_value: Any
    value: Any

    @property
    def selected_value(self):
        if self.data_type is list:
            return self.default_value[self.value]
        return self.value


@dataclasses.dataclass
class DataSetState:
    _name: str
    active: bool = True
    display: bool = False

    @property
    def name(self):
        return self._name
