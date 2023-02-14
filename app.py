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
import nanodata as nano


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
    except Exception as e:
        print(e)


def extract_zip(file_name: str, dir_name: str) -> None:
    try:
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(dir_name)
    except Exception as e:
        print(e)


def generate_raw_curve_plt(stack, segment: int):
    fig, ax = plt.subplots()
    ax.plot(stack[segment].z, stack[segment].f)
    ax.set(xlabel="z (nm)", ylabel="Force (nN)", title="Force vs Z")
    ax.grid()
    fig.set_size_inches(8, 5)
    return fig


def generate_raw_curve(data_man, segment: int):
    # takes a list of experiments and returns a list of experiment dataframes for the selected segment
    exp_data_frames = []

    for internal in data_man:
        print("here "+ internal.name)
        df = pd.DataFrame(
            {
                "z": internal.segments[segment].z,
                "f": internal.segments[segment].force,
                "exp": internal.path,
            }
        )
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


def save_to_json(experiments):
    ref = experiments[0].haystack[0]
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
        .mark_line()
        .encode(
            x="z:Q",
            y="f:Q",
        )
        .interactive()
    )
    return base


def layer_charts(data_frames, chart_func):
    # takes a list of pandas dataframes and a chart function and returns a layered chart
    layers = [chart_func(data_frame) for data_frame in data_frames]
    return alt.layer(*layers)


def file_handler(file_name: str, quale: str, experiments: list, file):
    # takes a file name, a string indicating the type of file, a list of experiments and a file object
    # and returns a list of experiments with the new file added
    if file_name.endswith(".zip"):
        experiments = nano.NanoDataManager("/" + file_name)
        experiments.preload()
        print(experiments.path)
    else:
        dir_name = tempfile.mkdtemp()  # create a temp folder to pass to experiment
        save_uploaded_file(file, dir_name)  # save the file to the temp folder
        # experiments.append(get_experiment(dir_name, quale))
        experiments = nano.NanoDataManager( dir_name)
        experiments.preload()
    return experiments


def threshold_filter(experiments: list, threshold: float):
    threshold = threshold * 1e-9

    for stack in experiments[0].haystack:
        for segment in stack:
            if np.max(segment.f) < threshold:
                segment.active = False
            else:
                segment.active = True


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
    right_graph_title.write("Additional Curve")

    left_config_title.write("Global Config")
    left_config_segment.selectbox(
        "Segment",
        ("NA",),
    )

    right_config_col.write("Additional Config")
    data_type = right_config_col.selectbox(
        "Data type",
        ("deflection", "force", "indentation", "time", "z"),
    )

    # Filter GUI elements
    select_filter = st.selectbox(
        "Filter",
        ("--select--", "Threshold"),
    )

    if file is not None:
        experiments = []
        save_uploaded_file(file, "data")
        fname = "data/" + file.name
        experiments = file_handler(fname, quale, experiments, file)
        print(len(experiments))

        segment = left_config_segment.selectbox(
            "Segment", (i for i in range(4))
        )

        if save_json_button:
            save_to_json(experiments)
            with open('data/test.json') as f:
                file_select_col.download_button('Download JSON', data=f, file_name='test.json')

        raw_curve = generate_raw_curve(experiments, segment)

        # make a layered altair chart with each curve from raw_curve as a layer

        left_graph.altair_chart(
            layer_charts(raw_curve, base_chart), use_container_width=True
        )
        right_graph.altair_chart(layer_charts(raw_curve, base_chart), use_container_width=True)

        # Execute filters
        if select_filter == "Threshold":
            threshold = st.text_input("Force Threshold (nN)", 0.0)
            threshold_filter(experiments, float(threshold))


if __name__ == "__main__":
    main()
