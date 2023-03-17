import streamlit as st
from misc import *
import nanodata as nd


class UI(st.delta_generator.DeltaGenerator, metaclass=UISingleton):
    def __init__(self):
        super().__init__()
        self._sidebar = UISideBar(self)
        self._graphs: dict[str, UIGraph] = {}
        self._manager = nd.ChiaroDataManager(tempfile.mkdtemp())
        self._data_sets: dict[str, DataSetState] = {
            data_set.name: DataSetState(data_set.name) for data_set in self._manager
        }
