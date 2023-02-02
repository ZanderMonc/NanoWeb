from contextlib import contextmanager

import pytest
import time
from playwright.sync_api import Page, expect
import numpy as np


@pytest.fixture(scope="module", autouse=True)
def before_module():
    # Run the streamlit app before each module
    with run_streamlit():
        yield


@pytest.fixture(scope="function", autouse=True)
def before_test(page: Page):
    page.goto(f"localhost:{8509}")


@contextmanager
def run_streamlit():
    import subprocess
    p = subprocess.Popen(["streamlit", "run", "app.py","--server.port", "8509","--server.headless", "true", ])
    time.sleep(5)
    try:
        yield 1
    finally:
        p.kill()


def test_default_screenshots(page: Page):
    time.sleep(3)
    page.screenshot(path="tests/data/default.png")
    expect(page).to_have_title("NanoWeb")
    assert 1 == 1

def test_upload(page: Page):
    # Test that the upload works
    page.screenshot(path="tests/data/upload1.png")
    #compare shape and bitwise xor
    assert np.array_equal(np.array(open("tests/data/default.png","rb").read()), np.array(open("tests/data/upload1.png", "rb").read())) == False
    page.click("text=Browse files")
    page.set_input_files("input[type=file]", "tests/data/inden.zip")
    time.sleep(2)
    page.screenshot(path="tests/data/upload2.png")
    expect(page).to_have_title("NanoWeb")
    assert np.array(open("tests/data/default.png","rb").read()) != np.array(open("tests/data/upload2.png", "rb").read())


if __name__ == "__main__":
    pytest.main()

