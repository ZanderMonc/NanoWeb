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
    p = subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8509", "--server.headless", "true", ])
    time.sleep(5)
    try:
        yield p
    finally:
        p.kill()


def test_default_screenshots(page: Page):
    time.sleep(3)
    # if default screenshot is not taken before test is ran, take it
    try:
        open("tests/data/default_homepage.png", "rb").read()
    except FileNotFoundError:
        page.screenshot(path="tests/data/default_homepage.png")
    expect(page).to_have_title("NanoWeb")
    assert 1 == 1

def test_homepage(page: Page):
    try:
        open("tests/data/test_homepage.png", "rb").read()
    except FileNotFoundError:
        time.sleep(3)
        page.screenshot(path="tests/data/test_homepage.png")
    # compare shape and bitwise xor
    assert np.array_equal(np.array(open("tests/data/default_homepage.png", "rb").read()), np.array(open("tests/data/test_homepage.png", "rb").read()))

def test_upload_changes(page: Page):
    page.click("text=Browse files")
    page.set_input_files("input[type=file]", "tests/data/smallest.zip")
    time.sleep(2)
    page.screenshot(path="tests/data/test_upload_change.png")
    # first assert that the view has changed vew input files
    assert not np.array_equal(np.array(open("tests/data/test_homepage.png", "rb").read())
                              ,np.array(open("tests/data/test_upload_change.png", "rb").read()))
def test_upload_accuracy(page : Page):
    page.click("text=Browse files")
    page.set_input_files("input[type=file]", "tests/data/inden.zip")
    time.sleep(4)
    try:
        open("tests/data/upload_expected_accuracy.png", "rb").read()
        page.screenshot(path="tests/data/test_upload_change2.png")
    except FileNotFoundError:#if no default screenshot is taken, take it and then when test is reran it will be compared
        page.screenshot(path="tests/data/upload_expected_accuracy.png")
        page.screenshot(path="tests/data/test_upload_change2.png")

    # assert that the view is the same as the expected view
    assert np.array_equal(np.array(open("tests/data/upload_expected_accuracy.png", "rb").read())
                          ,np.array(open("tests/data/test_upload_change2.png", "rb").read()))



if __name__ == "__main__":
    pytest.main()
