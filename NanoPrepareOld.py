import tempfile
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import os
import mvexperiment.experiment as experiment
import numpy as np
import zipfile
import matplotlib.pyplot as plt
import pandas as pd
import json
import altair as alt
import nanodata.nanodata as nano


def get_selection(title: str, options: tuple | list) -> str:
    """Creates a selection box element in the GUI with a given title and options
        Args:
            title (str): title of selection box
            options (tuple[any] or list[any]): options for the selection

        Returns:
            any: option selected from the selection inputted to GUI
    """
    return st.selectbox(
        title,
        options,
    )


@st.cache
def save_uploaded_file(uploaded_file: UploadedFile, path: str) -> None:
    """Saves the contents of an uploaded file to a given path.

        Args:
            uploaded_file (UploadedFile): File uploaded using the streamlit file uploader
            path (str): The path to the directory where the file will be saved

    """
    try:
        file_name: str = uploaded_file.name
        with open(os.path.join(path, file_name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        print(f"Saved File:{file_name} to {path}")
    except Exception as e:
        print(e)


def extract_zip(file_name: str, dir_name: str) -> None:
    """Extracts the contents of the zip file to a given directory.

        Args:
            file_name (str): Name of the zip file
            dir_name (str): The path to the directory where the file will be extracted

    """
    try:
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(dir_name)
        return True
    except Exception as e:
        print(e)


def generate_raw_curve(experiment_manager: iter, segment: int, ratio_z_left: float = 1, ratio_z_right: float = 1):
    """Creates DataFrame objects for experiment data in a given segment and returns them in a list

        Args:
            experiment_manager (iter): iterable DataManager object
            segment (int): Number corresponding to a certain segment
            ratio_z_left (float): Left-hand side limit for specifying a certain range of z values
            ratio_z_right (float): Right-hand side limit for specifying a certain range of z values

        Returns:
            exp_data_frames (list): list of DataFrame objects
    """


def generate_raw_curve(
        data_man, segment: int, ratio_z_left: float = 1, ratio_z_right: float = 1
):
    # takes a list of experiments and returns a list of experiment dataframes for the selected segment
    exp_data_frames = []

    for internal in data_man:

        df = pd.DataFrame(
            {
                "z": internal.segments[segment].z,
                "f": internal.segments[segment].force,
                "exp": internal.path,
            }
        )

        if ratio_z_left != 1 or ratio_z_right != 1:
            # crop the dataframe to only the z data range
            # df = df[df["z"] < ratio * np.max(df["z"])]
            df = df[df["z"] > ratio_z_left * np.min(df["z"])]
            df = df[df["z"] < ratio_z_right * np.max(df["z"])]

        exp_data_frames.append(df)

    return exp_data_frames


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


def save_to_json(active_datasets):
    """Saves the data of active datasets to a JSON file.

            Args:
                active_datasets (iter): list of datasets
    """

    fname = "data/test.json"

    curves = []

    for dataset in active_datasets:
        for i, segment in enumerate(dataset):
            cv = generate_json_template()
            cv["filename"] = dataset.name[dataset.name.rindex('/')+1:] + f"_{i+1}"
            cv["tip"]["radius"] = dataset.tip_radius * 1e-9
            cv["spring_constant"] = dataset.cantilever_k
            cv["speed"] = segment.speed
            cv["data"]["F"] = segment.data['force'].tolist()
            cv["data"]["Z"] = segment.data['z'].tolist()

            curves.append(cv)

    exp = {"Description": "Optics11 data"}
    pro = {}

    json_contents = json.dumps({"experiment": exp, "protocol": pro, "curves": curves}, indent="")

    with open(fname, "w") as f:
        f.write(json_contents)


def base_chart(data_frame):
    """Creates a base layer for a layered chart from a given DataFrame object

            Args:
                data_frame: DataFrame object

            Returns:
                base: Chart object corresponding to the base layer
    """
    base = (
        alt.Chart(
            data_frame,
        )
        .mark_line(point=True, thickness=1)
        .encode(
            x="z:Q",
            y="f:Q",
            tooltip=["z:Q", "f:Q", "exp:N"],
        )
        .interactive()
    )
    return base


def layer_charts(data_frames: list, chart_func):
    """Layers individual charts created from DataFrame objects in a given list

            Args:
                data_frames (list): list of DataFrame objects
                chart_func: Function creating a single layer of the layered chart

            Returns:
                layered_charts: A layered chart
    """
    layers = [chart_func(data_frame) for data_frame in data_frames]
    layered_charts = alt.layer(*layers)
    return layered_charts


def file_handler(file_name: str, quale: str, file: UploadedFile):
    """Decides how to handle the uploaded file and creates an experiment manager storing its data

            Args:
                file_name (str): Name of the file to be handled
                file (UploadedFile): File uploaded using the streamlit file uploader

            Returns:
                experiment_manager (iter): iterable DataManager object
    """
    if file_name.endswith(".zip"):
        # unzip the file
        dir_name = tempfile.mkdtemp()  # create a temp folder to pass to experiment
        extract_zip(file_name, dir_name)  # save the file to the temp folder
        experiment_manager = nano.ChiaroDataManager(dir_name)
        experiment_manager.load()
        print(experiment_manager.path)
    else:
        dir_name = tempfile.mkdtemp()  # create a temp folder to pass to experiment
        save_uploaded_file(file, dir_name)  # save the file to the temp folder
        # experiment_manager.append(get_experiment(dir_name, quale))
        experiment_manager = nano.ChiaroDataManager(dir_name)
        experiment_manager.load()
        print(experiment_manager.path)
    return experiment_manager


def get_filter(filter_name: str):
    for supported_filter in nano.filters:
        if supported_filter.name == filter_name:
            return supported_filter
        else:
            return None


def execute_filter(experiment_manager, filter_object, params) -> list:
    active_datasets = []
    for dataset in experiment_manager:
        if filter_object.is_valid(params, dataset):
            active_datasets.append(dataset)
    return active_datasets


def main() -> None:
    st.set_page_config(
        layout="wide", page_title="NanoWeb", page_icon="images/cellmech.png"
    )
    top_bar = st.container()
    file_select_col, file_upload_col = top_bar.columns(2)

    graph_bar = st.container()
    left_graph_col, right_graph_col = graph_bar.columns(2)
    left_graph_title = left_graph_col.empty()
    right_graph_title = right_graph_col.empty()
    left_graph = left_graph_col.empty()
    right_graph = right_graph_col.empty()

    config_bar = st.container()
    left_config_col, right_config_col = config_bar.columns(2)
    left_config_title = left_config_col.empty()
    left_config_segment = left_config_col.empty()
    right_config_title = right_config_col.empty()
    right_config_segment = right_config_col.empty()
    right_config_segment2 = right_config_col.empty()

    quale = file_select_col.selectbox(
        "File type",
        (
            "Optics11",
            "Optics11_2019",
            "Optics11_OLD",
            "Nanosurf",
            "TSV",
            "jpk-force",
            "jpk-fmap",
        ),
    )

    save_json_button = file_select_col.button("Save to JSON")
    file = file_upload_col.file_uploader("Choose a zip file")

    left_graph.line_chart()
    left_graph_title.write("Raw Curve")

    right_graph.line_chart()
    right_graph_title.write("Cropped Curve")

    left_config_title.write("Global Config")
    left_config_segment.selectbox(
        "Segment",
        ("NA",),
    )

    right_config_title.write("Additional Config")
    ratio_z_left = right_config_segment.slider("crop left", 0.0, 1.0, 0.5, 0.01)
    ratio_z_right = right_config_segment2.slider("crop right", 0.0, 1.0, 0.5, 0.01)

    # Filter GUI elements
    select_filter = st.selectbox(
        "Filter",
        ("--select--", "Threshold"),
    )

    if file is not None:
        save_uploaded_file(file, "data")
        fname = "data/" + file.name
        experiment_manager = file_handler(fname, quale, file)
        if 'active_datasets' not in st.session_state:
            st.session_state['active_datasets'] = experiment_manager.data_sets

        st.session_state['active_datasets'] = experiment_manager.data_sets

        segment = left_config_segment.selectbox(
            "Segment", (i for i in range(len(list(experiment_manager.data_sets)[0])))
        )

        if save_json_button:
            save_to_json(st.session_state['active_datasets'])
            with open("data/test.json") as f:
                file_select_col.download_button(
                    "Download JSON", data=f, file_name="test.json"
                )

        raw_curve = generate_raw_curve(experiment_manager, segment)

        # make a layered altair chart with each curve from raw_curve as a layer

        left_graph.altair_chart(
            layer_charts(raw_curve, base_chart), use_container_width=True
        )

        # use the right graph to lense in on the left graph, where the cursor hovers on the left graph the right
        # graph shows a zoomed in view
        right_graph.altair_chart(
            layer_charts(
                generate_raw_curve(
                    experiment_manager, segment, ratio_z_left, ratio_z_right
                ),
                base_chart,
            ),
            use_container_width=True,
        )

        # Execute filters
        if select_filter == "Threshold":
            threshold = st.text_input("Force Threshold (nN)", -1.0)
            force_filter = get_filter("Force Filter")

            # run filter
            if force_filter:
                filtered_data = execute_filter(experiment_manager,
                                               force_filter,
                                               {"force": float(threshold),
                                                "comparison": ">"})
                st.session_state['active_datasets'] = filtered_data

                print(f"Filter applied for threshold {threshold}")
                print(len(experiment_manager.data_sets))
                print(len(st.session_state['active_datasets']))

                # re-generate the raw curve
                raw_curve = generate_raw_curve(filtered_data, segment)

                # re-generate the left graph
                left_graph.altair_chart(
                    layer_charts(raw_curve, base_chart), use_container_width=True
                )

                # re-generate the right graph
                right_graph.altair_chart(
                    layer_charts(
                        generate_raw_curve(
                            filtered_data, segment, ratio_z_left, ratio_z_right
                        ),
                        base_chart,
                    ),
                    use_container_width=True,
                )
            else:
                st.warning("Threshold filter is not currently initialised.")
        else:
            st.session_state['active_datasets'] = experiment_manager.data_sets


if __name__ == "__main__":
    main()
