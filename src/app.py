import altair as alt
import shiny
from shinywidgets import output_widget, render_altair
import pandas as pd

data = pd.read_csv("data/raw/tech_employment_2000_2025.csv")

companies = sorted(data['company'].unique())
years = sorted(data['year'].unique())

DEFAULT_COMPANY = [companies[0]] if companies else []
DEFAULT_YEAR_MIN = int(min(years)) if years else 2000
DEFAULT_YEAR_MAX = int(max(years)) if years else 2025

companies_ui = shiny.ui.input_selectize(
    "company",
    "Select Companies:",
    choices=companies,
    selected=DEFAULT_COMPANY,
    multiple=True
)

years_ui = shiny.ui.input_slider(
    "year",
    "Select Year Range:",
    min=DEFAULT_YEAR_MIN,
    max=DEFAULT_YEAR_MAX,
    value=[DEFAULT_YEAR_MIN, DEFAULT_YEAR_MAX],
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
        shiny.ui.value_box(shiny.ui.output_text("ratio_title"), shiny.ui.output_text("hire_layoff_ratio")),
        shiny.ui.value_box(shiny.ui.output_text("metric_title"), shiny.ui.output_text("total_hires")),
        shiny.ui.value_box("Total Layoffs", shiny.ui.output_text("total_layoffs")),
    ),
    title="Layoff Lens: Tech Workforce Dashboard"
)


def server(input, output, session):

    @shiny.reactive.calc
    def filtered_df():
        company_val = input.company()
        selected = list(company_val) if company_val else []
        yr = input.year()
        if not selected:
            return data.head(0)
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
        metric = input.hiring_metric()
        
        if df_plot.empty:
            return alt.Chart(pd.DataFrame()).mark_text().encode(text=alt.value("Select a company to see trends"))

        metric_label = HIRING_METRICS.get(metric, metric)
        y_title = "Rate (%)" if metric == "hiring_rate_pct" else "Number of People"

        chart = alt.Chart(df_plot).mark_line(point=True).encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y(f"{metric}:Q", title=f"{metric_label}"),
            color="company:N",
            tooltip=["company", "year", metric]
        ).properties(
            width="container",
            height=400
        ).interactive()

        return chart

    @shiny.render.text
    def ratio_title():
        metric = input.hiring_metric()
        if metric == "hiring_rate_pct":
            return "Avg Hiring Rate"
        return f"{HIRING_METRICS.get(metric, metric)} / Layoff Ratio"

    @shiny.render.text
    def metric_title():
        metric = input.hiring_metric()
        label = HIRING_METRICS.get(metric, metric)
        if metric == "hiring_rate_pct":
            return f"Avg {label}"
        return f"Total {label}"

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
    
    @shiny.reactive.effect
    @shiny.reactive.event(input.reset)
    async def reset_filters():
        shiny.ui.update_selectize(
            "company",
            choices=companies,
            selected=DEFAULT_COMPANY,
            session=session,
        )
        shiny.ui.update_slider(
            "year",
            value=[DEFAULT_YEAR_MIN, DEFAULT_YEAR_MAX],
            session=session,
        )
        shiny.ui.update_select(
            "hiring_metric",
            selected="net_change",
            session=session,
        )


app = shiny.App(app_ui, server)
