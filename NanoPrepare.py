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
    return st.selectbox(
        title,
        options,
    )


def get_experiment(dir_name: str, file_type: str):
    if file_type == "Optics11":
        exp = experiment.Chiaro(dir_name)
    elif file_type == "Optics11_2019":
        exp = experiment.Chiaro2019(dir_name)
    elif file_type == "Optics11_OLD":
        exp = experiment.ChiaroGenova(dir_name)
    elif file_type == "Nanosurf":
        exp = experiment.NanoSurf(dir_name)
    elif file_type == "TSV":
        exp = experiment.Easytsv(dir_name)
    elif file_type == "jpk-force":
        exp = experiment.Jpk(dir_name)
    elif file_type == "jpk-fmap":
        exp = experiment.JpkForceMap(dir_name)
    else:
        exp = None

    if exp is not None:
        exp.browse()

        if not len(exp):
            raise FileNotFoundError("No files found")
        return exp
    else:
        raise KeyError("Invalid experiment type")


@st.cache
def save_uploaded_file(uploaded_file: UploadedFile, path: str) -> None:
    try:
        file_name: str = uploaded_file.name
        with open(os.path.join(path, file_name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        print(f"Saved File:{file_name} to {path}")
        return path
    except Exception as e:
        print(e)


def extract_zip(file_name: str, dir_name: str) -> None:
    try:
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(dir_name)
        print("Extracting zip file", file_name, "to", dir_name)
        return True
    except Exception as e:
        print(e)
        return False


def generate_raw_curve_plt(stack, segment: int):
    fig, ax = plt.subplots()
    ax.plot(stack[segment].z, stack[segment].f)
    ax.set(xlabel="z (nm)", ylabel="Force (nN)", title="Force vs Z")
    ax.grid()
    fig.set_size_inches(8, 5)
    return fig


def generate_raw_curve(
    data_man, segment: int, ratio_z_left: float = 1, ratio_z_right: float = 1
):
    # takes a list of experiments and returns a list of experiment dataframes for the selected segment
    exp_data_frames = []

    for internal in data_man:
        # check that z and force are not none
        if np.any(internal.segments[segment].z == 0) or np.any(
            internal.segments[segment].force == 0
        ):
            # if segment is dead, do not process it and break;
            st.warning(
                "Segment "
                + str(segment)
                + " has a curve out of threshold that has been ignored"
            )
            break

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


def generate_empty_curve():
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


def save_to_json(experiment_manager):
    ref = experiment_manager[0].haystack[0]
    curves = []
    fname = "data/test.json"

    geometry = ref.tip_shape
    radius = ref.tip_radius
    spring = ref.cantilever_k

    for segment in ref:
        if segment.active:
            cv = generate_empty_curve()
            # cv["filename"] = segment.basename
            cv["tip"]["radius"] = radius * 1e-9
            cv["tip"]["geometry"] = geometry
            cv["spring_constant"] = spring
            # cv["position"] = (segment.xpos, segment.ypos)
            cv["data"]["Z"] = list(segment.z * 1e-9)
            cv["data"]["F"] = list(segment.f * 1e-9)
            curves.append(cv)

    exp = {"Description": "Optics11 data"}
    pro = {}

    json.dump({"experiment": exp, "protocol": pro, "curves": curves}, open(fname, "w"))


def base_chart(data_frame):
    # produces a chart to be used as a layer in a layered chart
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


def layer_charts(data_frames, chart_func):
    # takes a list of pandas dataframes and a chart function and returns a layered chart
    layers = [chart_func(data_frame) for data_frame in data_frames]
    return alt.layer(*layers)


def file_handler(file_name: str, file):
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


def threshold_filter(experiment_manager, threshold: float):
    for internal in experiment_manager:
        for segment in internal.segments:
            if segment.force is not None:
                # if max force is over threshold, set force and z to 0
                if max(segment.force) < threshold:
                    segment.set_force(0)
                    segment.set_z(0)


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

        segment = left_config_segment.selectbox(
            "Segment", (i for i in range(len(list(experiment_manager.data_sets)[0])))
        )

        if save_json_button:
            save_to_json(experiment_manager)
            with open("data/test.json") as f:
                file_select_col.download_button(
                    "Download JSON", data=f, file_name="test.json"
                )

        raw_curve = generate_raw_curve(experiment_manager, segment)

        # make a layered altair chart with each curve from raw_curve as a layer

        left_graph.altair_chart(
            layer_charts(raw_curve, base_chart), use_container_width=True
        )

        # use the right graph to lense in on the left graph, where the cursor hovers on the left graph the right graph shows a zoomed in view
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
            threshold = st.text_input("Force Threshold (nN)", -1)
            threshold_filter(experiment_manager, float(threshold))
            # for threshold filter, remove non-active segments from the dataset
            # then re-generate the raw curve
            raw_curve = generate_raw_curve(experiment_manager, segment)
            # then re-generate the left graph
            left_graph.altair_chart(
                layer_charts(raw_curve, base_chart), use_container_width=True
            )
            # then re-generate the right graph
            right_graph.altair_chart(
                layer_charts(
                    generate_raw_curve(
                        experiment_manager, segment, ratio_z_left, ratio_z_right
                    ),
                    base_chart,
                ),
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
