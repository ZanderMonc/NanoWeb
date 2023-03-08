from typing import Any
import abc
import numpy as np
from . import abstracts
import re


class FilterMeta(abc.ABCMeta, type):
    _filters: dict[type, "Filter"] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        new_cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if abc.ABC not in bases:
            mcs._filters[new_cls] = new_cls()

        return new_cls

    @staticmethod
    def filters() -> list["Filter"]:
        return list(FilterMeta._filters.values())


class FilterParameter:
    def __init__(
        self, name: str, data_type: type, description: str, default_value: Any
    ):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.default_value = default_value

    def __repr__(self):
        return f"FilterParameter({self.name}, {self.data_type.__name__}, {self.description}, {self.default_value})"


class Filter(abc.ABC, metaclass=FilterMeta):
    """Class for creating filters to filter data sets.

    This is the base class to be used in all filter implementations.
    super() should be called with a description of your filter.
    After, the add_parameter method should be called for each parameter you wish to add.

    Args:
        description (str): human-readable description of the filter
    """
    def __init__(self, description: str):
        self.name = self.__create_name()
        self.description = description
        self.parameters: list[FilterParameter] = []

    def add_parameter(
        self, name: str, data_type: type, description: str, default_value: Any
    ):
        """Adds a parameter to the filter.

        Args:
            name (str): name of the parameter
            data_type (type): type of the parameter (e.g. int, float, str, list)
            description (str): human-readable description of the parameter
            default_value (Any): default value of the parameter to be displayed initially in UI
        """
        self.parameters.append(
            FilterParameter(name, data_type, description, default_value)
        )

    def __create_name(self) -> str:
        return " ".join(re.findall("[A-Z][^A-Z]*", type(self).__name__))

    @abc.abstractmethod
    def is_valid(self, parameters: dict[str, Any], data_set: abstracts.DataSet) -> bool:
        """Checks if a data set is valid for the filter.

        Args:
            parameters (dict): dictionary of parameters to be used to determine if the data set is valid
            data_set (DataSet): data set to be checked

        Returns:
            bool: true if the data set is valid, False otherwise
        """
        ...

    @staticmethod
    def filters() -> list["Filter"]:
        return FilterMeta.filters()

    def __repr__(self):
        return f"{type(self).__name__}({self.name}, {self.description}, {self.parameters})"


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
