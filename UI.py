import streamlit as st
import tempfile
import nanodata.nanodata as nd
import abc
import pandas as pd
import altair as alt
from typing import Any
from enum import Enum
import dataclasses
import zipfile
import json

def generate_json_template():
    """Generates a JSON formatting template corresponding to the data of a sample curve

        Returns:
            curve (dict): A dictionary formatted for JSON filetype for a sample curve
    """
    curve = {
        "filename": "noname",
        "date": "2021-12-02",
        "device_manufacturer": "Optics11",
        "tip": {"geometry": "sphere", "radius": 0.0},
        "spring_constant": 0.0,
        "segment": "approach",
        "speed": 0.0,
        "data": {"F": [], "Z": []},
    }
    return curve

class UISingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(UISingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataSetVars(Enum):
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


class UI(st.delta_generator.DeltaGenerator, metaclass=UISingleton):
    def __init__(self):
        super().__init__()
        self._sidebar = UISideBar(self)
        self._graphs: dict[str, UIGraph] = {}
        self._manager = nd.ChiaroDataManager(tempfile.mkdtemp())
        self._data_sets: dict[str, DataSetState] = {
            data_set.name: DataSetState(data_set.name) for data_set in self._manager
        }

    def draw(self):
        self.__run_config()
        # upload zip file and set manager path to tempfile path
        file = self.file_uploader("Upload zipped data files", type="zip")
        save_json_button = self.button("Save to JSON")

        if file is not None:
            with zipfile.ZipFile(file, "r") as zip_file:
                zip_file.extractall(self.manager.path)

        if save_json_button:
            self.export_json()
            with open("data/test.json") as f:
                self.download_button(
                    "Download JSON", data=f, file_name="test.json"
                )

        self.sidebar.draw()
        self.draw_graphs()



    def add_graph(self, x_field: str, y_field: str):
        self._graphs[f"{x_field}-{y_field}"] = UIGraph(self, x_field, y_field)

    def remove_graph(self, x_field: DataSetVars, y_field: DataSetVars):
        del self._graphs[f"{x_field}-{y_field}"]

    def draw_graphs(self):
        for graph in self.graphs.values():
            graph.draw()

    def load_data_sets(self):
        self.manager.load()
        self._data_sets: dict[str, DataSetState] = {
            data_set.name: DataSetState(data_set.name) for data_set in self._manager
        }

    def export_json(self):
        """Saves the data of active datasets to a JSON file."""

        fname = "data/test.json"

        curves = []

        for dataset_name in self.data_sets:
            dataset_obj = self.manager[dataset_name]
            if self.data_sets[dataset_name].active:
                for i, segment in enumerate(dataset_obj):
                    cv = generate_json_template()
                    cv["filename"] = dataset_obj.name + f"-{i + 1}"
                    cv["tip"]["radius"] = dataset_obj.tip_radius * 1e-9
                    cv["spring_constant"] = dataset_obj.cantilever_k
                    cv["speed"] = segment.speed
                    cv["data"]["F"] = segment.data['force'].tolist()
                    cv["data"]["Z"] = segment.data['z'].tolist()

                    curves.append(cv)

        exp = {"Description": "Optics11 data"}
        pro = {}

        json_contents = json.dumps({"experiment": exp, "protocol": pro, "curves": curves}, indent="")

        with open(fname, "w") as f:
            f.write(json_contents)

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
            options=[var.value for var in DataSetVars],
            index=3,
        )
        y_field = col2.selectbox(
            "Y Field",
            options=[var.value for var in DataSetVars],
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


class UISideBar(UIElement):
    def __init__(self, window: UI):
        super().__init__(window)
        self._sidebar = st.sidebar
        self.data_sets_container = DataSetsContainer(self)
        self.graphs_container = GraphsContainer(self)
        self.filters_container = FiltersContainer(self)

    def write(self, *args, **kwargs) -> None:
        self.sidebar.write(*args, **kwargs)

    def header(self, *args, **kwargs) -> None:
        self.sidebar.header(*args, **kwargs)

    def button(self, *args, **kwargs) -> bool:
        return self.sidebar.button(*args, **kwargs)

    def number_input(self, *args, **kwargs) -> int | float:
        return self.sidebar.number_input(*args, **kwargs)

    def slider(self, *args, **kwargs) -> Any:
        return self.sidebar.slider(*args, **kwargs)

    def selectbox(self, *args, **kwargs) -> Any:
        return self.sidebar.selectbox(*args, **kwargs)

    def columns(self, *args, **kwargs) -> Any:
        return self.sidebar.columns(*args, **kwargs)

    def expander(self, title: str) -> st.delta_generator.DeltaGenerator:
        return self.sidebar.expander(title)

    def draw(self):
        self.header("Data Manager")
        self.write(f"Loaded Data Sets: {len(self.window.manager)}")
        self.button("Load Data Sets", on_click=self.window.load_data_sets)

        self.data_sets_container.draw()
        self.graphs_container.draw()
        self.filters_container.draw()

    @property
    def sidebar(self):
        return self._sidebar


class UIGraph(UIElement):
    def __init__(self, window: UI, x_field: str, y_field: str):
        super().__init__(window)
        self._x_field = x_field
        self._y_field = y_field
        self._data_frames: dict[str, pd.DataFrame] = {}

    def write(self, *args, **kwargs) -> None:
        pass

    def header(self, *args, **kwargs) -> None:
        pass

    def button(self, *args, **kwargs) -> bool:
        pass

    def number_input(self, *args, **kwargs) -> int | float:
        pass

    def slider(self, *args, **kwargs) -> Any:
        pass

    def selectbox(self, *args, **kwargs) -> Any:
        pass

    def columns(self, *args, **kwargs) -> Any:
        pass

    def expander(self, title: str) -> st.delta_generator.DeltaGenerator:
        pass

    def draw(self):
        total_data_points = sum(len(data_frame) for data_frame in self.data_frames)

        self.window.write(f"Total Data Points: {total_data_points}")
        self.window.altair_chart(
            self.__layer_charts(self.data_frames), use_container_width=True
        )

    def __base_chart(self, data_frame):
        color = (
            "cyan"
            if self.window.data_sets[data_frame["experiment"][0]].active
            else "red"
        )
        base = (
            alt.Chart(
                data_frame,
            )
            .mark_line(point=False, thickness=1, color=color)
            .encode(
                x=f"{self._x_field}:Q",
                y=f"{self._y_field}:Q",
                tooltip=[f"{self._x_field}:Q", f"{self._y_field}:Q", "experiment:N"],
            )
            .interactive()
        )

        return base

    def __layer_charts(self, data_frames):
        layers = [self.__base_chart(data_frame) for data_frame in data_frames]

        return alt.layer(*layers)

    def add_data_frame(self, data_name: str, data_frame: pd.DataFrame):
        self._data_frames[data_name] = data_frame

    def remove_data_frame(self, data_name: str):
        if data_name in self._data_frames:
            del self._data_frames[data_name]

    @property
    def data_frames(self) -> list[pd.DataFrame]:
        return list(self._data_frames.values())
