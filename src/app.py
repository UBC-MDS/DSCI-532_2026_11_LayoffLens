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
    selected=companies[0],
    multiple=True
)

years_ui = shiny.ui.input_slider(
    "year",
    "Select Year Range:",
    min=min(years),
    max=max(years),
    value=[min(years), max(years)],
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

reset_ui = shiny.ui.input_action_button(
    "reset",
    "Reset All Filters",
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
        shiny.ui.hr(), 
        shiny.ui.help_text(
            "Note: High hiring spikes can precede consolidation. Use the Hire-Layoff ratio to assess long-term stability."
        ),
        reset_ui,
    ),
    shiny.ui.card(
        shiny.ui.card_header("Company Hiring & Layoff Trends"),
        output_widget("company_trend_plot"),
    ),
    shiny.ui.card(
        shiny.ui.card_header("Company Revenue in Billions USD"),
        output_widget("revenue_in_billions"),
    ),
    shiny.ui.layout_columns(
        shiny.ui.value_box("Hire-Layoff Ratio", shiny.ui.output_text("hire_layoff_ratio")),
        shiny.ui.value_box("Total Hires", shiny.ui.output_text("total_hires")),
        shiny.ui.value_box("Total Layoffs", shiny.ui.output_text("total_layoffs")),
    ),
    title="Layoff Lens: Tech Workforce Dashboard"
)


def server(input, output, session):

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
    def revenue_in_billions():
        df_plot = filtered_df()

        if df_plot.empty:
            return alt.Chart(pd.DataFrame()).mark_text().encode(text=alt.value("Select a company to see revenue in billions"))
        
        chart = alt.Chart(df_plot).mark_bar().encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("revenue_billions_usd:Q", title="Revenue by Year (Billions USD)"),
            color="company:N",
            tooltip=["company", "year", "revenue_billions_usd"]
        ).properties(
            width="container",
            height=400
        ).interactive()

        return chart
    
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

    @shiny.render.text
    def hire_layoff_ratio():
        filtered_data = filtered_df()
        if filtered_data.empty:
            return "Hire-Layoff Trend Not Available"

        total_hires = filtered_data.loc[:,"new_hires"].sum()
        total_layoffs = filtered_data.loc[:, "layoffs"].sum()

        if total_hires == 0 or total_layoffs == 0:
            return "Hire-Layoff Ratio Not Available"
        
        return f"Hire-Layoff Ratio: {total_hires / total_layoffs:.2f}"
    
    @shiny.render.text
    def total_hires():
        filtered_data = filtered_df()
        total_hires = filtered_data.loc[:, "new_hires"].sum()
        if filtered_data.empty:
            return "Total Hires Not Available"
        
        return f"Total Hires: {total_hires}"
    
    @shiny.render.text
    def total_layoffs():
        filtered_data = filtered_df()
        total_layoffs = filtered_data.loc[:, "layoffs"].sum()
        if filtered_data.empty:
            return "Total Layoffs Not Available"
        
        return f"Total Layoffs: {total_layoffs}"
    
    # Optional complexity feature that resets all filters
    @shiny.reactive.effect
    @shiny.reactive.event(input.reset)
    def reset_filters():
        shiny.ui.update_selectize("company", selected=[])
        shiny.ui.update_slider("year", value=[min(years), max(years)])
        shiny.ui.update_select("hiring_metric", selected="net_change")


app = shiny.App(app_ui, server)
