# Author: Chris Greening
# Date: 02/03/2021
# Purpose: US energy consumption app

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly
import pandas as pd

import data_processing as dp
import plot_computations as pc
import plotting
import markdown

DEBUG = True

df = dp.load_dataset()
primary_energy_df = dp.load_primary_energy_sources(df)

# Precomputed figures
us_primary_bar_dict = pc.us_primary_per_year(primary_energy_df)
us_primary_pie_dict = pc.us_primary_per_year_pie(primary_energy_df)

external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

if not DEBUG:
    server = app.server

app.layout = html.Div(children = [
    html.Div(
        children = [
            html.H1("United States Energy Consumption", style={"font-size": "6vh", "text-align": "center"}),
            dcc.Markdown(markdown.INTRO),
            html.Hr(),
            html.Div(
                children = [
                    html.Div(
                        html.Div(
                            children=[
                                html.H3(
                                    "Total energy consumption",
                                    className="plot-header"
                                ),
                                dcc.Graph(
                                    id="us-total",
                                    figure=pc.us_total(df, primary_energy_df),
                                    hoverData={"points": [{"x": "2018-01-01"}]},
                                    style={"height": plotting.PLOT_HEIGHT}
                                )
                            ],
                            className="plot"
                        ),
                        className="col-xl-8"
                    ),
                    html.Div(
                        html.Div(
                            children=[
                                html.H3(
                                    id="us-primary-header",
                                    className="plot-header"
                                ),
                                dcc.Graph(
                                    id="us-primary-bar",
                                    style={"height": plotting.PLOT_HEIGHT}
                                )
                            ],
                            className="plot"
                        ),
                        className="col-xl-4"
                    )
                ],
                className="row"
            ),
            html.Div(
                children = [
                    html.Div(
                        html.Div(
                            children=[
                                html.H3(
                                    "Resource usage",
                                    className="plot-header"
                                ),
                                dcc.Graph(
                                    id="us-total-stacked-area",
                                    figure=pc.us_total_stacked_area(
                                        primary_energy_df),
                                    style={"height": plotting.PLOT_HEIGHT},
                                    hoverData={"points": [
                                        {"x": 2018}]},
                                )
                            ],
                            className="plot"
                        ),
                        className="col-xl-8 order-xl-12"
                    ),
                    html.Div(
                        html.Div(
                            children=[
                                html.H3(
                                    id="us-primary-pie-header",
                                    className="plot-header"
                                ),
                                dcc.Graph(
                                    id="us-primary-pie",
                                    style={"height": plotting.PLOT_HEIGHT}
                                )
                            ],
                            className="plot"
                        ),
                        className="col-xl-4 order-xl-1"
                    ),
                ],
                className="row"
            )
        ],
        className="container-fluid dash"
    )
])


########## HEADERS
@app.callback(
    Output('us-primary-pie-header', 'children'),
    Input('us-total-stacked-area', 'hoverData')
)
def us_primary_pie_header(hoverData):
    year_value = int(hoverData['points'][0]['x'])
    return f"Resource usage ({year_value})"


@app.callback(
    Output('us-primary-header', 'children'),
    Input('us-total', 'hoverData')
)
def us_primary_bar_header(hoverData):
    year_value = int(hoverData['points'][0]['x'][:4])
    return f"Total energy consumption ({year_value})"

########## BAR PLOT

@app.callback(
    Output('us-primary-bar', 'figure'),
    Input('us-total', 'hoverData')
)
def us_primary_bar(hoverData):
    year_value = int(hoverData['points'][0]['x'][:4])
    fig = us_primary_bar_dict[year_value]
    return fig

@app.callback(
    Output('us-primary-pie', 'figure'),
    Input('us-total-stacked-area', 'hoverData')
)
def us_primary_pie(hoverData):
    year_value = int(hoverData['points'][0]['x'])
    fig = us_primary_pie_dict[year_value]
    return fig


if __name__ == '__main__':
    app.run_server(debug=DEBUG)
