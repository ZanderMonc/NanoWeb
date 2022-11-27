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


def save_uploaded_file(uploaded_file: UploadedFile):
    try:
        file_name: str = uploaded_file.name
        with open(os.path.join("data", file_name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved File:{file_name} to data", icon="✅")

    except Exception as e:
        st.error(e, icon="❌")


def main() -> None:
    quale = st.selectbox(
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
    file = st.file_uploader("Choose a zip file")
    if file is not None:
        save_uploaded_file(file)
        fname = "data/" + file.name
        with zipfile.ZipFile(fname, "r") as zip_ref:
            zip_ref.extractall("data")
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
