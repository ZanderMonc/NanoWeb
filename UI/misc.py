from enum import StrEnum


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
