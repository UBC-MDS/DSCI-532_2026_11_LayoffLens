import altair as alt
import shiny
from shinywidgets import output_widget, render_altair
from shiny import render
import pandas as pd
import ibis
import querychat
from chatlas import ChatGithub
from dotenv import load_dotenv
from pathlib import Path

con = ibis.duckdb.connect()

data_path = Path(__file__).parent.parent / "data" / "processed" / "tech_employment_2000_2025.parquet"

all_data = con.read_parquet(data_path)

data = all_data.mutate(
    net_change_pct=(all_data["employees_end"] / all_data["employees_start"] * 100) - 100
).drop(
    "is_estimated", "confidence_level", "data_quality_score"
)

companies = sorted(data.select("company").distinct().to_pandas()["company"].tolist())
years = sorted(data.select("year").distinct().to_pandas()["year"].tolist())

SELECTED_DEFAULT_COMPANIES = ["Amazon", "Apple", "Alphabet", "Meta", "Microsoft"]
DEFAULT_COMPANY = [c for c in SELECTED_DEFAULT_COMPANIES if c in companies]
DEFAULT_YEAR_MIN = int(min(years)) if years else 2000
DEFAULT_YEAR_MAX = int(max(years)) if years else 2025

load_dotenv(Path(__file__).parent.parent / ".env")

qc = querychat.QueryChat(
    data.execute(),
    "Company_Workforce",
    greeting="""👋 Ask me anything about the workforce data.

* <span class="suggestion">Show only AMD</span>
* <span class="suggestion">Filter to companies who grew in 2025</span>
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
    "net_change_pct": "Net Change %",
}

hiring_metric_ui = shiny.ui.input_select(
    "hiring_metric",
    "Hiring Metric:",
    choices=HIRING_METRICS,
    selected="net_change_pct"
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
        shiny.ui.help_text("Tip: Click and drag on charts to zoom; double-click to reset view."),
        shiny.ui.hr(),
        shiny.ui.help_text(
            "Note: High hiring spikes can precede consolidation. Use the Hire-Layoff ratio to assess long-term stability."
        )
    ),
    shiny.ui.navset_card_tab(
        # --- TAB 1: EXISTING DASHBOARD ---
        shiny.ui.nav_panel(
            "Company Insights",
            shiny.ui.layout_columns(
                shiny.ui.value_box(
                    shiny.ui.output_text("ratio_title"), 
                    shiny.ui.output_text("hire_layoff_ratio"),
                    theme="primary",
                ),
                shiny.ui.value_box(
                    shiny.ui.output_text("metric_title"), 
                    shiny.ui.output_text("total_hires"),
                    theme="success",
                ),
                shiny.ui.value_box(
                    "Total Layoffs", 
                    shiny.ui.output_text("total_layoffs"),
                    theme="danger",
                ),
            ),
            shiny.ui.layout_columns(
                shiny.ui.card(
                    shiny.ui.card_header("Workforce Trends"),
                    output_widget("company_trend_plot"),
                ),
                shiny.ui.card(
                    shiny.ui.card_header("Revenue (Billions USD)"),
                    output_widget("revenue_in_billions"),
                ),
                col_widths=[7, 5]
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
            ),
            shiny.ui.layout_columns(
                shiny.ui.card(
                    shiny.ui.card_header("Workforce Trends"),
                    output_widget("chat_hiring_layoff_chart"),
                ),
                shiny.ui.card(
                    shiny.ui.card_header("Revenue (Billions USD)"),
                    output_widget("chat_revenue_chart"),
                ),
                col_widths=[7, 5],
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

    def _empty_chart(message):
        return alt.Chart(pd.DataFrame()).mark_text().encode(
            text=alt.value(message)
        )

    @output
    @render_altair
    def chat_hiring_layoff_chart():
        df_full = qc_vals.df()
        required = {"year", "company", "net_change_pct"}
        if df_full.empty or not required.issubset(df_full.columns):
            return _empty_chart("QueryChat's DataFrame does not contain the required columns")

        df_plot = df_full.head(10)

        companies_in = df_plot["company"].unique()
        if len(companies_in) > 3:
            comp_str = f"{len(companies_in)} Companies"
        else:
            comp_str = ", ".join(sorted(companies_in))

        unique_years = df_plot["year"].nunique()

        if unique_years <= 1:
            return alt.Chart(df_plot).mark_bar().encode(
                x=alt.X("company:N", title="Company", sort="-y"),
                y=alt.Y("net_change_pct:Q", title="Net Change (%)", axis=alt.Axis(format=".1f")),
                color="company:N",
                tooltip=["company", "year", alt.Tooltip("net_change_pct:Q", format=".1f")],
            ).properties(
                title=f"Net Change % for {comp_str} ({df_plot['year'].iloc[0]})",
                width="container",
                height=350,
            ).interactive()

        return alt.Chart(df_plot).mark_line(point=True).encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("net_change_pct:Q", title="Net Change (%)", axis=alt.Axis(format=".1f")),
            color="company:N",
            tooltip=["company", "year", alt.Tooltip("net_change_pct:Q", format=".1f")],
        ).properties(
            title=f"Net Change % Trends for {comp_str}",
            width="container",
            height=350,
        ).interactive()

    @output
    @render_altair
    def chat_revenue_chart():
        df_full = qc_vals.df()
        required = {"year", "company", "revenue_billions_usd"}
        if df_full.empty or not required.issubset(df_full.columns):
            return _empty_chart("Requires: year, company, revenue_billions_usd")

        df_plot = df_full.head(10)

        order = (
            df_plot.groupby("company", as_index=False)["revenue_billions_usd"]
            .sum()
            .sort_values("revenue_billions_usd", ascending=False)["company"]
            .tolist()
        )

        return alt.Chart(df_plot).mark_bar().encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("revenue_billions_usd:Q", title="Revenue by Year (Billions USD)"),
            color=alt.Color("company:N", legend=None, sort=order),
            order=alt.Order("revenue_billions_usd:Q", sort="descending"),
            tooltip=["company", "year", "revenue_billions_usd"],
        ).properties(
            width="container",
            height=350,
        ).interactive()

    @shiny.reactive.calc
    def filtered_df():
        company_val = input.company()
        yr = input.year()

        selected = list(company_val) if company_val else DEFAULT_COMPANY

        return data.filter([
            data["company"].isin(selected),
            data["year"].between(yr[0], yr[1])
        ])
    
    @output
    @render_altair
    def revenue_in_billions():
        df_plot = filtered_df().to_pandas()

        if df_plot.empty:
            return alt.Chart(pd.DataFrame()).mark_text().encode(text=alt.value("Select a company to see revenue in billions"))
        
        chart = alt.Chart(df_plot).mark_bar().encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("revenue_billions_usd:Q", title="Revenue by Year (Billions USD)"),
            color=alt.Color("company:N", legend=None),
            tooltip=["company", "year", "revenue_billions_usd"]
        ).properties(
            width="container",
            height=400
        ).interactive()

        return chart
    
    @output
    @render_altair
    def company_trend_plot():
        df_plot = filtered_df().to_pandas()
        metric = input.hiring_metric()
        metric_label = HIRING_METRICS.get(metric, metric)   

        selected_companies = input.company()
        if len(selected_companies) > 3:
            comp_str = f"{len(selected_companies)} Companies"
        else:
            comp_str = ", ".join(selected_companies)
            
        chart_title = f"{metric_label} Trends for {comp_str} ({input.year()[0]}-{input.year()[1]})"
        
        if df_plot.empty:
            return alt.Chart(pd.DataFrame()).mark_text().encode(text=alt.value("Select a company to see trends"))

        metric_label = HIRING_METRICS.get(metric, metric)
        
        if "pct" in metric:
            y_title = f"{metric_label} (%)"
            y_format = ".1f" 
        else:
            y_title = f"{metric_label} (Total)"
            y_format = ","

        chart = alt.Chart(df_plot).mark_line(point=True).encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y(f"{metric}:Q", title=y_title, axis=alt.Axis(format=y_format)),
            color="company:N",
            tooltip=["company", "year", alt.Tooltip(f"{metric}:Q", format=y_format)]
        ).properties(
            title=chart_title,
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
        if filtered_data.count().execute() == 0:
            return "Hire-Layoff Trend Not Available"

        total_hires = filtered_data["new_hires"].sum().execute()
        total_layoffs = filtered_data["layoffs"].sum().execute()

        if not total_hires or not total_layoffs:
            return "Hire-Layoff Ratio Not Available"
        
        return f"Hire-Layoff Ratio: {total_hires / total_layoffs:,.2f}"
    
    @shiny.render.text
    def total_hires():
        filtered_data = filtered_df()
        
        total_hires = filtered_data["new_hires"].sum().execute()

        if total_hires is None:
            return "Total Hires Not Available"
        
        return f"Total Hires: {total_hires:,}"
    
    @shiny.render.text
    def total_layoffs():
        filtered_data = filtered_df()

        total_layoffs = filtered_data["layoffs"].sum().execute()

        if total_layoffs is None:
            return "Total Layoffs Not Available"
        
        return f"Total Layoffs: {total_layoffs:,}"
    
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
            selected="net_change_pct",
            session=session,
        )

    @shiny.render.download(filename="layoff_lens_data.csv")
    def download_data():
        df = qc_vals.df()
        if df is not None:
            yield df.to_csv(index=False)
            

app = shiny.App(app_ui, server)
