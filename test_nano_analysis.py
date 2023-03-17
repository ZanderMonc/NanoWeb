import os.path
import pages.NanoAnalysis as NanoAnalysis
import NanoPrepare as NanoPrepare



def test_file_is_json():
    f = open("tests/prepare_export.json", "r")
    assert NanoAnalysis.file_is_json(f) is True
    f.close()
def test_file_is_not_json():
    f = open("tests/smallest.zip", "r")
    assert NanoAnalysis.file_is_json(f) is False
    f.close()

def test_file_is_not_none():
    f = open("tests/smallest.zip", "r")
    assert NanoAnalysis.file_not_none(f) is True
    f.close()

def test_file_is_none():
    f = None
    assert NanoAnalysis.file_not_none(f) is False

def test_generate_raw_curves():
    pass

def test_generate_raw_curves_with_empty_haystack():
    pass

