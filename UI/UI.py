import streamlit as st
from misc import *
import tempfile
import nanodata as nd
import abc


class UI(st.delta_generator.DeltaGenerator, metaclass=UISingleton):
    def __init__(self):
        super().__init__()
        self._sidebar = UISideBar(self)
        self._graphs: dict[str, UIGraph] = {}
        self._manager = nd.ChiaroDataManager(tempfile.mkdtemp())
        self._data_sets: dict[str, DataSetState] = {
            data_set.name: DataSetState(data_set.name) for data_set in self._manager
        }

    @property
    def sidebar(self):
        return self._sidebar

    @property
    def graphs(self):
        return self._graphs

    @property
    def manager(self):
        return self._manager

    @property
    def data_sets(self) -> dict[str, DataSetState]:
        return self._data_sets

    @staticmethod
    def __run_config():
        st.set_page_config(
            layout="wide",
            page_title="NanoWeb",
            page_icon="images/cellmech.png",
            menu_items={
                "Get Help": None,
                "Report a Bug": None,
                "About": "Web version of CellMechLabs NanoPrepare and NanoAnalysis tools\n"
                "Ported by: GU 3rd Year CompSci students @SH32\n"
                "\nGithub: https://github.com/CellMechLab/",
            },
        )


class UIElement(abc.ABC):
    def __init__(self, window: UI):
        self._window = window

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def write(self, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def header(self, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def button(self, *args, **kwargs) -> bool:
        pass

    @abc.abstractmethod
    def number_input(self, *args, **kwargs) -> int | float:
        pass

    @abc.abstractmethod
    def slider(self, *args, **kwargs) -> Any:
        pass

    @abc.abstractmethod
    def selectbox(self, *args, **kwargs) -> Any:
        pass

    @abc.abstractmethod
    def columns(self, *args, **kwargs) -> Any:
        pass

    @abc.abstractmethod
    def expander(self, title: str) -> Any:
        pass

    @property
    def window(self):
        return self._window


class ContainerUtils(abc.ABC):
    def __init__(self, parent: UIElement, expander_title: str):
        self._parent = parent
        self._expander = None
        self._expander_title = expander_title

    def write(self, *args, **kwargs) -> None:
        self.parent.write(*args, **kwargs)

    def header(self, *args, **kwargs) -> None:
        self.parent.header(*args, **kwargs)

    def button(self, *args, **kwargs) -> bool:
        return self.parent.button(*args, **kwargs)

    def number_input(self, *args, **kwargs) -> int | float:
        return self.parent.number_input(*args, **kwargs)

    def slider(self, *args, **kwargs) -> Any:
        return self.parent.slider(*args, **kwargs)

    def selectbox(self, *args, **kwargs) -> Any:
        return self.parent.selectbox(*args, **kwargs)

    def columns(self, *args, **kwargs) -> Any:
        return self.parent.columns(*args, **kwargs)

    def draw(self):
        self._expander = self.parent.expander(self._expander_title)

    @property
    def parent(self):
        return self._parent

    @property
    def window(self):
        return self.parent.window

    @property
    def manager(self):
        return self.window.manager

    @property
    def data_sets(self):
        return self.window.data_sets

    @property
    def expander(self):
        return self._expander

    @property
    def expander_title(self):
        return self._expander_title
