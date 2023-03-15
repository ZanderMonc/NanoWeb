import tempfile

import NanoPrepare as NanoPrepare
import nanodata.nanodata

f = open("tests/smallest.zip", "rb")
file_name = "tests/smallest.zip"

print("Here: ", isinstance(NanoPrepare.file_handler(file_name, f), nanodata.nanodata.ChiaroDataManager))
# print("Hello world")