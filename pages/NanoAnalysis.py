import calendar
import tempfile
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
import shutil
import altair as alt
import nanodata
import nanodata.nano as nano
from NanoPrepare import save_uploaded_file
import nanoanalysisdata.engine as engine


def main() -> None:
    st.set_page_config(
        layout="wide", page_title="NanoWeb", page_icon="../images/cellmech.png"
    )

    top_bar = st.container()
    file = top_bar.file_uploader("Upload a JSON file")

    if file is not None:
        if file.name.endswith(".json"):
            save_uploaded_file(file, "data")

            # Load the JSON file
            f = open("data/" + file.name, "r")
            structure = json.load(f)
            # st.write(structure)
            for cv in structure["curves"]:
                engine.haystack.append(engine.curve(cv))


        else:
            st.warning("Only files with the .json extension are supported.")

    


if __name__ == "__main__":
    main()
