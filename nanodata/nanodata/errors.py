import inspect
import os


class DataSetExistsError(Exception):
    pass


class DataSetNotFoundError(Exception):
    pass


class DataSetTypeExistsError(Exception):
    pass
