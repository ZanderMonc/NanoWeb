import streamlit as st
from misc import *
import tempfile
import nanodata as nd
import abc
import pandas as pd


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


class DataSetsContainer(ContainerUtils):
    def __init__(self, parent: "UISideBar"):
        super().__init__(parent, "Data Sets")

    def draw(self):
        super().draw()
        if len(self.manager) == 0:
            self.expander.write("No data sets loaded")
            return

        segment_index = self.number_input(
            "Segment",
            min_value=0,
            max_value=len(self.manager[0]) - 1,
            value=0,
            step=1,
        )
        name_title, checkbox_title = self.expander.columns(2)
        with name_title:
            st.write("Data Set")
        with checkbox_title:
            st.write("In View")

        for (
            data_set_name,
            data_set_properties,
        ) in self.data_sets.items():
            name, checkbox = self.expander.columns(2)
            with name:
                st.write(data_set_name)
            with checkbox:
                if st.checkbox(
                    " ", value=data_set_properties.display, key=data_set_name
                ):
                    self._add_data_set_to_graph(data_set_name, segment_index)
                else:
                    self._remove_data_set_from_graph(data_set_name)

    def _add_data_set_to_graph(self, data_set_name: str, segment_index: int):
        data_set = self.manager[data_set_name]
        for graph_name, graph in self.window.graphs.items():
            x_field, y_field = graph_name.split("-")

            graph.add_data_frame(
                data_set_name,
                self._create_data_frame(data_set, segment_index, x_field, y_field),
            )

    def _remove_data_set_from_graph(self, data_set_name: str):
        for graph in self.window.graphs.values():
            graph.remove_data_frame(data_set_name)

    @staticmethod
    def _create_data_frame(data_set: nd.TDataSet, segment_index: int, x_field, y_field):
        return pd.DataFrame(
            {
                x_field: data_set[segment_index][x_field],
                y_field: data_set[segment_index][y_field],
                "experiment": data_set.name,
            }
        )


class GraphsContainer(ContainerUtils):
    def __init__(self, parent: "UISideBar"):
        super().__init__(parent, "Graphs")

    def draw(self):
        super().draw()
        if not self.window.graphs:
            self.expander.write("No graphs added")
        else:
            x_title, y_title, remove_title = self.expander.columns(3)
            with x_title:
                st.write("X Field")
            with y_title:
                st.write("Y Field")

            for graph_name, graph in self.window.graphs.items():
                x_field, y_field = graph_name.split("-")
                x, y, remove = self.expander.columns(3)

                with x:
                    st.write(x_field)
                with y:
                    st.write(y_field)
                with remove:
                    st.button(
                        "X",
                        key=graph_name,
                        on_click=self.window.remove_graph,
                        args=(x_field, y_field),
                    )

        col1, col2 = self.columns(2)
        x_field = col1.selectbox(
            "X Field",
            options=[var for var in DataSetVars],
            index=3,
        )
        y_field = col2.selectbox(
            "Y Field",
            options=[var for var in DataSetVars],
            index=1,
        )

        self.button(
            "Add Graph",
            on_click=self.window.add_graph,
            args=(x_field, y_field),
        )


class FiltersContainer(ContainerUtils):
    def __init__(self, parent: "UISideBar"):
        super().__init__(parent, "Filters")
        self._filters: dict[nd.Filter, list[UserFilterParameter]] = {}

    def draw(self):
        super().draw()

        with self.expander:
            if not self.filters:
                st.write("No filters added")
            else:
                for filter, filter_params in self.filters.items():
                    st.write(filter.name)
                    for parameter in filter_params:
                        if parameter.data_type is list:
                            parameter.value = parameter.default_value.index(
                                st.selectbox(
                                    parameter.name,
                                    options=parameter.default_value,
                                    index=parameter.value,
                                )
                            )
                        elif parameter.data_type is int or parameter.data_type is float:
                            parameter.value = st.number_input(
                                parameter.name,
                                value=parameter.value,
                                step=1,
                            )

        selected_filter_name = self.selectbox(
            "Filter", options=[filter.name for filter in nd.filters]
        )

        col1, col2 = self.columns(2)

        col1.button(
            "Add Filter", on_click=self.__add_filter, args=(selected_filter_name,)
        )

        col2.button("Run Filters", on_click=self.__run_filters)

    def __add_filter(self, filter_name_to_add: str):
        # add filter with matching name
        parameters: list[UserFilterParameter] = []
        for filter in nd.filters:
            if filter.name == filter_name_to_add:
                for parameter in filter.parameters:
                    if parameter.data_type is list:
                        parameters.append(
                            UserFilterParameter(
                                parameter.name,
                                parameter.data_type,
                                parameter.default_value,
                                0,
                            )
                        )
                    else:
                        parameters.append(
                            UserFilterParameter(
                                parameter.name,
                                parameter.data_type,
                                parameter.default_value,
                                parameter.default_value,
                            )
                        )

                self.filters[filter] = parameters
                break

    def __run_filters(self):
        if not self.filters:
            return
        for data_set in self.window.data_sets.values():
            for filter, filter_parameters in self.filters.items():
                parameters = {
                    filter_parameter.name: filter_parameter.selected_value
                    for filter_parameter in filter_parameters
                }
                data_set.active = filter.is_valid(
                    parameters, self.manager[data_set.name]
                )
                if not data_set.active:
                    break

    @property
    def filters(self):
        return self._filters
