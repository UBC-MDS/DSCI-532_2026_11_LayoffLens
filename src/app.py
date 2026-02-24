# Note: using the code from Ilya's DSCI 532 Lecture 3

import altair as alt
from shiny import App, ui
from shinywidgets import output_widget, render_altair

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
