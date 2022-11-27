import streamlit as st
import os
import sys
import mvexperiment.experiment as experiment
import numpy as np
import zipfile


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


def save_uploadedfile(uploadedfile):
    with open(os.path.join("data", uploadedfile.name), "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Saved File:{} to data".format(uploadedfile.name))


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
        save_uploadedfile(file)
        fname = "data/" + file.name
        with zipfile.ZipFile(fname, "r") as zip_ref:
            zip_ref.extractall("data")
        dir_name = "data/D-mode"

        exp = process(dir_name, quale)


if __name__ == "__main__":
    main()
