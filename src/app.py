# Note: using the code from Ilya's DSCI 532 Lecture 3

import altair as alt
from shiny import App, ui
from shinywidgets import output_widget, render_altair
import pandas as pd

data = pd.read_csv("data/raw/tech_employment_2000_2025.csv")

companies = sorted(data['company'].unique())
years = sorted(data['year'].unique())

companies_ui = ui.input_selectize(
    "company",
    "Select Companies:",
    choices=companies,
    multiple=True
)

years_ui = ui.input_slider(
    "year",
    "Select Year Range:",
    min=min(years),
    max=max(years),
    value=[2001, 2025], # Sets the default range handle positions
    sep="",             
    step=1
)

countries = alt.topo_feature(
    "https://vega.github.io/vega-datasets/data/world-110m.json",
    "countries",
)

app_ui = ui.page_fluid(
    ui.h4("World map (static geoshape)"),
    output_widget("map"),
)


def server(input, output, session):
    @output
    @render_altair
    def map():
        return (
            alt.Chart(countries)
            .mark_geoshape(stroke="white", strokeWidth=0.4)
            .encode(color=alt.value("#93C5FD"))
            .project(type="equalEarth")
            .properties(height=430)
        )


app = App(app_ui, server)
