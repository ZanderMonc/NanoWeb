import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import os
import sys
import mvexperiment.experiment as experiment
import numpy as np
import zipfile
import matplotlib.pyplot as plt
import pandas as pd
import json


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


def generate_raw_curve(stack, segment: int):
    test_curve = pd.DataFrame({"z": stack[segment].z, "f": stack[segment].f})
    test_curve = test_curve.set_index("z")

    return test_curve


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


def save_to_json(ref):
    curves = []
    fname = "data/test.json"
    print(len(ref))

    geometry = ref.tip_shape
    radius = ref.tip_radius
    spring = ref.cantilever_k

    for segment in ref:
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

    if file is not None:
        save_uploaded_file(file, "data")
        fname = "data/" + file.name
        extract_zip(fname, "data")
        # get extracted dir name
        dir_name = fname.replace(".zip", "")

        experiment = get_experiment(dir_name, quale)

        for c in experiment.haystack:
            c.open()

        ref = experiment.haystack[0]

        segment = left_config_segment.selectbox("Segment", (i for i in range(len(ref))))

        if save_json_button:
            save_to_json(ref)

        raw_curve = generate_raw_curve(ref, segment)

        left_graph.line_chart(raw_curve)
        right_graph.line_chart(ref.data[data_type])


if __name__ == "__main__":
    main()
