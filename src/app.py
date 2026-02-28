import altair as alt
import shiny
from shinywidgets import output_widget, render_altair
import pandas as pd

data = pd.read_csv("data/raw/tech_employment_2000_2025.csv")

companies = sorted(data['company'].unique())
years = sorted(data['year'].unique())

companies_ui = shiny.ui.input_selectize(
    "company",
    "Select Companies:",
    choices=companies,
    multiple=True
)

years_ui = shiny.ui.input_slider(
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

hiring_metric_ui = shiny.ui.input_select(
    "hiring_metric",
    "Hiring Metric:",
    choices=HIRING_METRICS,
)

countries = alt.topo_feature(
    "https://vega.github.io/vega-datasets/data/world-110m.json",
    "countries",
)

app_ui = shiny.ui.page_sidebar(
    shiny.ui.sidebar(
        shiny.ui.h2("Filters"),
        companies_ui,  
        years_ui,     
        hiring_metric_ui,
    ),
    shiny.ui.card(
        shiny.ui.card_header("Company Hiring & Layoff Trends"),
        output_widget("company_trend_plot"),
    ),
    shiny.ui.card(
        shiny.ui.card_header("Global View"),
        output_widget("map"),
    ),
    shiny.ui.layout_columns(
        shiny.ui.value_box("Hire-Layoff Ratio", shiny.ui.output_text("hire_layoff_ratio"),
    ),
    title="Tech Workforce Dashboard"
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

    @shiny.reactive.calc
    def filtered_df():
        selected = list(input.company())
        yr = input.year()
        return data[
            (data["company"].isin(selected))
            & (data["year"].between(yr[0], yr[1]))
        ]
    
    @output
    @render_altair
    def company_trend_plot():
        df_plot = filtered_df()
        
        if df_plot.empty:
            return alt.Chart(pd.DataFrame()).mark_text().encode(text=alt.value("Select a company to see trends"))

        df_melted = df_plot.melt(
            id_vars=['year', 'company'], 
            value_vars=['layoffs', 'new_hires'],
            var_name='Metric', 
            value_name='Count'
        )

        chart = alt.Chart(df_melted).mark_line(point=True).encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("Count:Q", title="Number of People"),
            color="company:N",
            strokeDash="Metric:N", 
            tooltip=["company", "year", "Metric", "Count"]
        ).properties(
            width="container",
            height=400
        ).interactive()

        return chart

    @render.text
    def hire_layoff_ratio():
        df = filtered_df()
        if df.empty:
            return "Hire-Layoff Trend Not Available"

        total_hires = df.loc[:,"new_hires"].sum()
        total_layoffs = df.loc[:, "layoffs"].sum()

        if total_hires == 0 or total_layoffs == 0:
            return "Hire-Layoff Ratio Not Available"
        else:
            return f"Hire-Layoff Ratio: {total_hires / total_layoffs:.2f}"


app = shiny.App(app_ui, server)
