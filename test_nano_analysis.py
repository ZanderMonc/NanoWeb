
import os.path
import pages.NanoAnalysis as NanoAnalysis
import NanoPrepare as NanoPrepare


# check if the file is a json file
def test_file_upload_checker_when_none():
    assert NanoAnalysis.file_upload_checker(None) is False


def test_file_upload_checker_when_a_none_json_file():
    f = open("tests/prepare_export.json", "r")
    assert NanoAnalysis.file_upload_checker(f) is True
    f.close()


def test_file_upload_checker_when_a_json_file():
    f = open("tests/smallest.zip", "r")
    assert NanoAnalysis.file_upload_checker(f) is False
    f.close()


def test_save_uploaded_file():
    print("Here : ", NanoPrepare.save_uploaded_file("tests/prepare_export.json", "data"))
    pass


