# Attribution: 
# https://shiny.posit.co/py/api/testing/playwright.controller.InputSelectize.html#shiny.playwright.controller.InputSelectize
# https://shiny.posit.co/py/api/testing/playwright.controller.InputSlider.html#shiny.playwright.controller.InputSlider

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from scripts.render_text import get_rendered_text
from playwright.sync_api import Page
from shiny.playwright import controller
from shiny.run import ShinyAppProc
from shiny.pytest import create_app_fixture
import pytest

app = create_app_fixture("../src/app.py")

filtered_data = pd.DataFrame({"year": [2010, 2012, 2014, 2016, 2018],
                              "new_hires": [1200, 4000, 3200, 10000, None],
                              "layoffs": [250, 1000, 1250, 400, 800]})

new_hires = filtered_data["new_hires"].sum()
layoffs = filtered_data["layoffs"].sum()

def test_get_rendered_text_empty():
    """
    This is an edge case test for when the summary statistic is
    based on empty df. We should expect the helper function to return 
    a string output with statistic value of 0

    """
    filter_df = filtered_data.query("year < 2010")
    new_hires = filter_df["new_hires"].sum()
    layoffs = filter_df["layoffs"].sum()

    assert len(filter_df) == 0
    assert get_rendered_text(filter_df, "new_hires", "New Hires") == "New Hires: 0.0"
    assert get_rendered_text(filter_df, "layoffs", "Layoffs") == "Layoffs: 0"

def test_get_rendered_text_basic():
    """
    This is a basic test to check whether our helper function provides
    the correct output given a filtered dataframe with summary statistics
    calculated and ready for rendering text

    """
    assert type(filtered_data) == pd.core.frame.DataFrame
    assert get_rendered_text(filtered_data, "new_hires", "New Hires") == "New Hires: 18,400.0"
    assert get_rendered_text(filtered_data, "layoffs", "Layoffs") == "Layoffs: 3,700"
    assert get_rendered_text(filtered_data.loc[4, :], "new_hires", "New Hires") == "New Hires: nan"

def test_get_rendered_text_missing_arg():
    """
    This is a test to check that the function will correctly
    return a TypeError if we do not provide one argument to it.
    Using pytest.raises() we check for the appropriate error
    
    """
    with pytest.raises(TypeError):
        get_rendered_text(filtered_data, "New Hires")

    with pytest.raises(TypeError):
        get_rendered_text("new_hires", "New Hires")

def test_basic_app_input(page: Page, app: ShinyAppProc):
    """
    This is the basic test for the app with a selection of
    company and a range of year. We want to check that the 
    expected output matches the input we set it to

    Checks:
        Selectize check for company
        Boundary Check for year
    
    """
    page.goto(app.url)

    selectize_company = controller.InputSelectize(page, "company")
    selectize_company.set("Amazon")
    selectize_company.expect_selected(["Amazon"])

    selectize_year = controller.InputSliderRange(page, "year")
    selectize_year.set(("2001", "2025"))
    selectize_year.expect_step(("1"))
    selectize_year.expect_min(("2001"))
    selectize_year.expect_max(("2025"))
    selectize_year.expect_value(("2001", "2025"))

def test_basic_app_edge_case(page: Page, app: ShinyAppProc):
    """
    This is the edge-case test for the app with no selection for
    company and single year. We want to check that the expected 
    output does not break with edge case inputs

    Checks:
        No selection check for company
        Edge-case filter check for year
    
    """
    page.goto(app.url)

    selectize_company = controller.InputSelectize(page, "company")
    selectize_company.set([])
    selectize_company.expect_selected([])

    selectize_year = controller.InputSliderRange(page, "year")
    selectize_year.set(("2015", "2015"))
    selectize_year.expect_step(("1"))
    selectize_year.expect_value(("2015", "2015"))
