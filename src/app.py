# Note: using the code from Ilya's DSCI 532 Lecture 3

import altair as alt
from shiny import App, ui
from shinywidgets import output_widget, render_altair
import pandas as pd
from shiny import reactive

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
    value=[2001, 2025],
    sep="",             
    step=1
)

HIRING_METRICS = {
    "net_change": "Net Change",
    "new_hires": "New Hires",
    "hiring_rate_pct": "Hiring Rate %",
}

hiring_metric_ui = ui.input_select(
    "hiring_metric",
    "Hiring Metric:",
    choices=HIRING_METRICS,
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

    @reactive.calc
    def filtered_df():
        selected = list(input.company())
        yr = input.year()
        return data[
            (data["company"].isin(selected))
            & (data["year"].between(yr[0], yr[1]))
        ]


app = App(app_ui, server)
