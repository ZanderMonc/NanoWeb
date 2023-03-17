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
import NanoPrepare as NanoPrepare
import nanodata.nanodata


def test_extract_zip():
    dir_name = tempfile.mkdtemp()
    file_name = "tests/smallest.zip"
    assert NanoPrepare.extract_zip(file_name, dir_name) is not None

def test_extract_zip_with_not_zip_file():
    dir_name = tempfile.mkdtemp()
    file_name = "tests/prepare_export.json"
    assert NanoPrepare.extract_zip(file_name, dir_name) is None

def test_file_handler():
    f = open("tests/smallest.zip", "rb")
    file_name = "tests/smallest.zip"
    assert isinstance(NanoPrepare.file_handler(file_name, f), nanodata.nanodata.ChiaroDataManager) is True

def test_threshold_filter():
    #TODO : add a test for the threshold filter when it is finished
    pass

def test_save_to_json():
    #TODO : add a test for the save to json when it is finished
    pass


def test_save_uploaded_file():
    # print("Here : ", NanoPrepare.save_uploaded_file("tests/prepare_export.json", "data"))
    pass


def test_generate_json_template():
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
    assert NanoPrepare.generate_json_template() == curve

