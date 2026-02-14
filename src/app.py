import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Layoff Lens"), width=12)
    ], className="mb-4 mt-4"),

    dbc.Row([
        # Sidebar for Filters
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters"),
                dbc.CardBody([
                    html.P("Year Selection:"),
                    dcc.RangeSlider(2020, 2025, step=1, value=[2020, 2025]),
                    html.Br(),
                    html.P("Industry Filter:"),
                    dcc.Dropdown(options=['Fintech', 'SaaS', 'AI'],
                                 multi=True, 
                                 placeholder="Select Industry")
                ])
            ])
        ], width=3),

        # Main Content Area
        dbc.Col([
            dbc.Row([
                # Card 1: Key Metric
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Layoffs", className="card-title"),
                        html.P("Placeholder: 124,000", className="text-danger")
                    ])
                ]), width=6),
                # Card 2: Key Metric
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H4("Net Job Change", className="card-title"),
                        html.P("Placeholder: +12,500", className="text-success")
                    ])
                ]), width=6),
            ], className="mb-4"),

            # Big Chart Placeholder
            dbc.Card([
                dbc.CardHeader("Hiring vs. Layoff Trends"),
                dbc.CardBody([
                    html.P("This card will display our interactive chart."),
                    dcc.Graph(id='placeholder-graph')
                ])
            ])
        ], width=9)
    ])
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)