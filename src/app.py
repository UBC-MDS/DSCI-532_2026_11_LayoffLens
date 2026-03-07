import altair as alt
import shiny
from shinywidgets import output_widget, render_altair
import pandas as pd
import querychat
from chatlas import ChatGithub
from dotenv import load_dotenv
from pathlib import Path
import os

data = pd.read_csv("data/raw/tech_employment_2000_2025.csv")
data = data.drop(
    ["is_estimated", "confidence_level", "data_quality_score"],
    axis=1
)

companies = sorted(data['company'].unique())
years = sorted(data['year'].unique())

DEFAULT_COMPANY = [companies[0]] if companies else []
DEFAULT_YEAR_MIN = int(min(years)) if years else 2000
DEFAULT_YEAR_MAX = int(max(years)) if years else 2025

load_dotenv(Path(__file__).parent.parent / ".env")

qc = querychat.QueryChat(
    data.copy(),
    "Company_Workforce",
    greeting="""👋 Ask me anything about the workforce data.

* <span class="suggestion">Show only AMD</span>
* <span class="suggestion">Filter to companies who grew in 2025</span>
* <span class="suggestion">Who paid the highest fare?</span>
* <span class="suggestion">Which companies shrunk in 2020?</span>
""",
    data_description="""
Workforce data of 25 companies from 2000-2025.
- company: Name of the technology company.
- year: Calendar year of the observation (mapped from fiscal year where applicable).
- employees_start: Number of employees at the beginning of the year.
- employees_end: Number of employees at the end of the year, primarily sourced from SEC 10-K filings.
- new_hires: Estimated number of employees hired during the year.
- layoffs: Number of publicly announced workforce reductions during the year (does not include natural attrition).
- net_change: Net change in employee count during the year (employees_end − employees_start).
- hiring_rate_pct: Hiring rate as a percentage of starting workforce size.
- attrition_rate_pct: Layoff rate as a percentage of starting workforce size.
- revenue_billions_usd: Annual company revenue expressed in billions of US dollars.
- stock_price_change_pct: Year-over-year percentage change in the company’s stock price
- gdp_growth_us_pct: Annual US GDP growth rate (percentage).
- unemployment_rate_us_pct: AnnQualitative confidence level for the data point (High, Medium, Low) based on source reliability.ual average US unemployment rate (percentage).
""",
    client = ChatGithub(model = "openai/gpt-4.1")
)

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
        reset_ui,
        shiny.ui.hr(), 
        shiny.ui.help_text(
            "Note: High hiring spikes can precede consolidation. Use the Hire-Layoff ratio to assess long-term stability."
        )
    ),
    shiny.ui.navset_card_tab(
        # --- TAB 1: EXISTING DASHBOARD ---
        shiny.ui.nav_panel(
            "Company Insights",
            shiny.ui.card(
                shiny.ui.card_header("Company Hiring & Layoff Trends"),
                output_widget("company_trend_plot"),
            ),
            shiny.ui.card(
                shiny.ui.card_header("Company Revenue in Billions USD"),
                output_widget("revenue_in_billions"),
            ),
            shiny.ui.layout_columns(
                shiny.ui.value_box(
                    shiny.ui.output_text("ratio_title"), 
                    shiny.ui.output_text("hire_layoff_ratio")
                ),
                shiny.ui.value_box(
                    shiny.ui.output_text("metric_title"), 
                    shiny.ui.output_text("total_hires")
                ),
                shiny.ui.value_box(
                    "Total Layoffs", 
                    shiny.ui.output_text("total_layoffs")
                ),
            ),
        ),
        
        # --- TAB 2: SKELETON FOR NEW TAB ---
        shiny.ui.nav_panel(
            "LLM Chat",
            shiny.ui.layout_sidebar(
            qc.sidebar(),
            shiny.ui.card(
                shiny.ui.card_header(shiny.ui.output_text("chat_title")),
                shiny.ui.output_data_frame("chat_table"),
                shiny.ui.download_button("download_data", "Download"),
                fill=True,
            ),
            fillable=True,
        ),
    ),
    ),
    title="Layoff Lens: Tech Workforce Dashboard"
)


def server(input, output, session):

    qc_vals = qc.server()

    @shiny.render.text
    def chat_title():
        return qc_vals.title() or "Employees dataset"

    @shiny.render.data_frame
    def chat_table():
        return qc_vals.df()

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

    @shiny.render.download(filename="layoff_lens_data.csv")
    def download_data():
        df = qc_vals.df()
        if df is not None:
            yield df.to_csv(index=False)
            

app = shiny.App(app_ui, server)
