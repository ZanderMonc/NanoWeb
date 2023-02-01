from contextlib import contextmanager
from playwright.sync_api import Page, expect

import playwright
import pytest
import time


@pytest.fixture(scope="module", autouse=True)
def before_module():
    # Run the streamlit app before each module
    with run_streamlit():
        yield


@pytest.fixture(scope="function", autouse=True)
def before_test(page: Page):
    page.goto(f"localhost:{8501}")


@contextmanager
def run_streamlit():
    import subprocess
    p = subprocess.Popen(["streamlit", "run", "app.py"])
    time.sleep(5)
    try:
        yield 1
    finally:
        p.kill()


def get_default_screenshots(page: Page):
    with run_streamlit():
        page.goto("http://localhost:8501")
        page.screenshot(path="tests/data/sample.png")
        page.setInputFiles("input[type=file]", "tests/data/2021-06-18-15-10-07.zip")
        page.click("text=Upload")
        page.waitForSelector("text=Experiment")
        page.screenshot(path="tests/data/sample_upload.png")


@pytest.mark.playwright
def test_display(self, browser):
    with run_streamlit():
        page = browser.newPage()
        page.goto("http://localhost:8501")
        page.screenshot(path="tests/data/screenshot.png")
    # check that screenshot is the same as sample
    expected = open("tests/data/sample.png", "rb").read()
    actual = open("tests/data/screenshot.png", "rb").read()
    assert expected == actual


def test_upload(self, browser):
    with run_streamlit():
        page = browser.newPage()
        page.goto("http://localhost:8501")
        page.setInputFiles("input[type=file]", "tests/data/2021-06-18-15-10-07.zip")
        page.click("text=Upload")
        page.waitForSelector("text=Experiment")
        page.screenshot(path="tests/data/screenshot_upload.png")
    # check that screenshot is the same as sample
    expected = open("tests/data/sample_upload.png", "rb").read()
    actual = open("tests/data/screenshot_upload.png", "rb").read()
    assert expected == actual


if __name__ == "__main__":
    # pytest.main()
    browser = playwright.chromium.launch()
    page = browser.newPage()
    get_default_screenshots()
