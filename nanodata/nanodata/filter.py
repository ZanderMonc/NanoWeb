from typing import Any
import abc
import numpy as np
from . import abstracts
import re


class FilterMeta(abc.ABCMeta, type):
    _filters: dict[type, "FilterMeta"] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        new_cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if abc.ABC not in bases:
            mcs._filters[new_cls] = new_cls

        return new_cls

    @staticmethod
    def filters() -> list["FilterMeta"]:
        return list(FilterMeta._filters.values())

    def __repr__(self):
        return f"{self.__name__}"


class FilterParameter:
    def __init__(
        self, name: str, data_type: type, description: str, default_value: Any
    ):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.default_value = default_value


class Filter(abc.ABC, metaclass=FilterMeta):
    def __init__(self, description: str):
        self.name = self.__create_name()
        self.description = description
        self.parameters: list[FilterParameter] = []

    def add_parameter(
        self, name: str, data_type: type, description: str, default_value: Any
    ):
        self.parameters.append(
            FilterParameter(name, data_type, description, default_value)
        )

    def __create_name(self) -> str:
        return " ".join(re.findall("[A-Z][^A-Z]*", type(self).__name__))

    @abc.abstractmethod
    def is_valid(self, parameters: dict[str, Any], data_set: abstracts.DataSet) -> bool:
        ...

    @staticmethod
    def filters() -> list[FilterMeta]:
        return FilterMeta.filters()


class ForceFilter(Filter):
    def __init__(self):
        super().__init__("Filters data sets depending on force limit")
        self.add_parameter("force", float, "Force limit", 1)
        self.add_parameter(
            "comparison", list, "Comparison", ["<", ">", "<=", ">=", "==", "!="]
        )

    def is_valid(self, parameters: dict[str, Any], data_set: abstracts.DataSet) -> bool:
        force_threshold = parameters["force"] * 1e-9
        comparison = parameters["comparison"]
        if comparison == "<":
            return np.max(data_set.force) < force_threshold
        elif comparison == "<=":
            return np.max(data_set.force) <= force_threshold
        elif comparison == ">=":
            return np.max(data_set.force) >= force_threshold
        elif comparison == "==":
            return np.max(data_set.force) == force_threshold
        elif comparison == "!=":
            return np.max(data_set.force) != force_threshold

        return np.max(data_set.force) > force_threshold
