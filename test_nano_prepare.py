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
from NanoPrepare import extract_zip


def test_file_handler():
    zip = "tests/data/smallest.zip"
    dirname = extract_zip(zip)
    file_handler = nano.ChiaroDataManager(dirname)
    assert file_handler is not None #TODO : check if the file handler is correct - typecheck

def test_threshold_filter():
    zip = "tests/data/smallest.zip"
    dirname = extract_zip(zip)
    file_handler = nano.ChiaroDataManager(dirname)
    #TODO : add a test for the threshold filter when it is finished
    pass

def test_save_to_json():
    zip = "tests/data/smallest.zip"
    dirname = extract_zip(zip)
    file_handler = nano.ChiaroDataManager(dirname)
    #TODO : add a test for the save to json when it is finished
    pass

def test_generate_empty_curve():
    empty = nano.generate_empty_curve()
    assert empty is not None #todo : check if the empty curve is correct - typecheck

def test_extract_zip():
    zip = "tests/data/smallest.zip"
    extract_zip(zip)#saves to tests/data/smallest by default
    with zipfile.ZipFile("tests/data/smallest.zip","tests/data/smallest2") as zip_ref:
        zip_ref.extractall("tests/data/smallest2")
    #assert contents of smallest2 is the same as smallest
    assert os.open("tests/data/smallest2", os.O_RDONLY) == os.open("tests/data/smallest", os.O_RDONLY) #todo check if this logic works
