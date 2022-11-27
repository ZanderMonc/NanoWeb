import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import os
import sys
import mvexperiment.experiment as experiment
import numpy as np
import zipfile
import matplotlib.pyplot as plt


def get_selection(title: str, options: tuple | list) -> str:
    return st.selectbox(
        title,
        options,
    )


def process(dir_name: str, quale: str):
    if "Optics11" in quale:
        if "2019" in quale:
            exp = experiment.Chiaro2019(dir_name)
        elif "OLD" in quale:
            exp = experiment.ChiaroGenova(dir_name)
        else:
            exp = experiment.Chiaro(dir_name)
    elif "Nanosurf" in quale:
        exp = experiment.NanoSurf(dir_name)
    elif "TSV" in quale:
        exp = experiment.Easytsv(dir_name)
    elif "jpk-force" in quale:
        exp = experiment.Jpk(dir_name)
    elif "jpk-fmap" in quale:
        exp = experiment.JpkForceMap(dir_name)

    exp.browse()

    if not len(exp):
        print("Error")

    return exp


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


def main() -> None:
    top_bar = st.container()
    file_select_col, file_upload_col = top_bar.columns(2)

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
    file = file_upload_col.file_uploader("Choose a zip file")
    if file is not None:
        save_uploaded_file(file, "data")
        fname = "data/" + file.name
        extract_zip(fname, "data")
        dir_name = "data/D-mode"

        experiment = process(dir_name, quale)

        for c in experiment.haystack:
            c.open()

        ref = experiment.haystack[0]

        segment = st.selectbox(
            "Segment",
            (seg for seg in range(len(ref))),
        )
        # deflection, force, indentation, time, z
        # st.header("Force")
        # st.line_chart(ref.data["force"])
        # st.header("Deflection")
        # st.line_chart(ref.data["deflection"])
        # st.header("Indentation")
        # st.line_chart(ref.data["indentation"])
        # st.header("Time")
        # st.line_chart(ref.data["time"])
        # st.header("Z")
        # st.line_chart(ref.data["z"])

        fig, ax = plt.subplots()
        ax.plot(ref[segment].z, ref[segment].f)
        ax.set(xlabel="z (nm)", ylabel="Force (nN)", title="Force vs Z")
        ax.grid()
        st.pyplot(fig)


if __name__ == "__main__":
    main()
