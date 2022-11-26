import streamlit as st
import os
import sys
# import mvexperiment.experiment as experiment
import numpy as np


def open_folder(root_name: str):
    pass


def save_uploadedfile(uploadedfile):
    with open(os.path.join("data", uploadedfile.name), "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Saved File:{} to data".format(uploadedfile.name))


def main() -> None:
    file = st.file_uploader("Choose a zip file")
    if file is not None:
        save_uploadedfile(file)


if __name__ == "__main__":
    main()
