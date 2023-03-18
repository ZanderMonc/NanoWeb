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
    quale = 'quale'
    assert isinstance(NanoPrepare.file_handler(file_name, quale, f), nanodata.nanodata.ChiaroDataManager) is True

def test_save_to_json():
    #TODO : add a test for the save to json when it is finished
    pass

def test_get_filter_with_existing_filter():
    assert isinstance(NanoPrepare.get_filter('Force Filter'), nanodata.nanodata.filter.ForceFilter) is True

def test_get_filter_with_none_existing_filter():
    assert NanoPrepare.get_filter('None existing filter') is None

def test_execute_filter():
    f = open("tests/smallest.zip", "rb")
    quale = 'quale'
    file_name = "tests/smallest.zip"
    data = NanoPrepare.file_handler(file_name, quale, f)
    filter_object = NanoPrepare.get_filter('Force Filter')
    threshold = 0.0
    params =  {"force": float(threshold),"comparison": ">"}

    assert len(NanoPrepare.execute_filter(data, filter_object, params)) == 3

def test_save_uploaded_file():
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

