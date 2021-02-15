# Author: Chris Greening
# Date: 02/03/2021
# Purpose: US energy consumption app

import json
import os

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

external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

df = dp.load_dataset()
primary_energy_df = dp.load_primary_energy_sources(df)
with open(os.path.join("data", "united_states.geojson")) as infile:
    united_states_geojson = json.load(infile)

# Precomputed figures
# us_main_plot_dict = pc.precompute_main_plots(df, primary_energy_df)
# state_total_dict = pc.precompute_state_per_year(df)

app.layout = html.Div(children = [
    # html.Div(
    #     children=[
    #         html.Div(
    #             dcc.Graph(
    #                 id="choropleth",
    #                 figure=pc.update_choropleth(df, united_states_geojson)
    #             ),
    #         ),
    #         dcc.Dropdown(
    #             id='year-slider',
    #             options=[{"value": year, "label": str(year)} for year in df["Year"].unique()],
    #             value=2018,
    #             style={"width" : "100px", "margin-left": "30px"}
    #         ),
    #     ]
    # ),
    html.Div(
        children = [
            html.H1("United States Energy Consumption", style={"font-size": "4vw", "text-align": "center"}),
            dcc.Markdown(markdown.INTRO, id="intro-text"),
            html.Hr(),
            html.Div(
                children = [
                    html.Div(
                        html.Div(
                            children=[
                                html.Div(
                                    children = [
                                        html.H3(
                                            id="main-plot-header",
                                            className="plot-header"
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {'label': 'Energy consumption',
                                                    'value': 'Energy consumption'},
                                                {'label': 'Energy consumption (per capita)',
                                                    'value': 'Energy consumption (per capita)'},
                                                {'label': 'Energy consumption (per resource)',
                                                    'value': 'Energy consumption (per resource)'},
                                                {'label': 'Resource consumption',
                                                    'value': 'Resource consumption'},
                                            ],
                                            value='Energy consumption',
                                            className="plot-type-dropdown",
                                            id="main-plot-type",
                                            clearable=False
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {'label': 'Year',
                                                    'value': 'Year'},
                                                {'label': 'President',
                                                    'value': 'President'},
                                            ],
                                            value='Year',
                                            id="x-axis-labels",
                                            clearable=False
                                        )
                                    ],
                                    className="row"
                                ),
                                dcc.Graph(
                                    id="us-total",
                                    clickData={"points": [{"x": "2018-01-01"}]},
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
                    ),
                ],
                className="row"
            ),
            html.Div(
                children = [
                    html.Div(
                        html.Div(
                            children=[
                                html.H3(
                                    id="us-pie-header",
                                    className="plot-header"
                                ),
                                dcc.Graph(
                                    id="us-primary-pie",
                                    style={"height": plotting.PLOT_HEIGHT}
                                )
                            ],
                            className="plot"
                        ),
                        className="col-xl-4"
                    ),
                    html.Div(
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.H3(
                                            id="state-plot-header",
                                            className="plot-header"
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {'label': 'Energy consumption',
                                                    'value': 'Energy consumption'},
                                                {'label': 'Energy consumption (per capita)',
                                                    'value': 'Energy consumption (per capita)'},
                                            ],
                                            value='Energy consumption',
                                            className="plot-type-dropdown",
                                            id="state-plot-type",
                                            clearable=False
                                        ),
                                    ],
                                    className="row"
                                ),
                                dcc.Graph(
                                    id="state-total-bar",
                                    style={"height": plotting.PLOT_HEIGHT}
                                )
                            ],
                            className="plot"
                        ),
                        className="col-xl-8"
                    ),
                ],
                className="row"
            ),
        ],
        className="container-fluid dash"
    )
])

########## HEADERS

@app.callback(
    Output('us-primary-header', 'children'),
    Input('us-total', 'clickData')
)
def us_primary_bar_header(clickData):
    year_value = int(clickData['points'][0]['x'][:4])
    return f"Resource usage ({year_value})"

@app.callback(
    Output('us-pie-header', 'children'),
    Input('us-total', 'clickData')
)
def us_primary_pie_header(clickData):
    year_value = int(clickData['points'][0]['x'][:4])
    return f"Resource % ({year_value})"

@app.callback(
    Output('main-plot-header', 'children'),
    Input("main-plot-type", "value"),
)
def update_main_plot_header(main_plot_type):
    return main_plot_type

@app.callback(
    Output('state-plot-header', 'children'),
    [Input("state-plot-type", "value"),
     Input('us-total', 'clickData')]
)
def update_state_plot_header(main_plot_type, clickData):
    year_value = int(clickData['points'][0]['x'][:4])
    return f"{main_plot_type} ({year_value})"

########## MAIN PLOT
@app.callback(
    Output('us-total', 'figure'),
    [Input("main-plot-type", "value"),
    Input("x-axis-labels", "value")]
)
def update_main_plot(depiction_type, x_axis_type):
    # fig_key = depiction_type + x_axis_type
    fig = pc.precompute_main_plots(df, primary_energy_df, depiction_type, x_axis_type)
    # fig = us_main_plot_dict[fig_key]
    return fig

########## PIE CHART

@app.callback(
    Output('us-primary-pie', 'figure'),
    Input('us-total', 'clickData')
)
def us_primary_pie(clickData):
    year_value = int(clickData['points'][0]['x'][:4])
    fig = pc.pie_plot_per_year(primary_energy_df, year_value)
    return fig

########## BAR PLOT

@app.callback(
    Output('us-primary-bar', 'figure'),
    Input('us-total', 'clickData')
)
def us_primary_bar(clickData):
    year_value = int(clickData['points'][0]['x'][:4])
    fig = pc.us_primary_per_year(primary_energy_df, year_value)
    return fig

@app.callback(
    Output('state-total-bar', 'figure'),
    [Input('state-plot-type', 'value'),
    Input('us-total', 'clickData')]
)
def update_state_bar_plot(state_plot_type, clickData):
    year_value = int(clickData['points'][0]['x'][:4])
    # dict_key = state_plot_type + str(year_value)
    # fig = state_total_dict[dict_key]
    fig = pc.precompute_state_per_year(df, primary_energy_df, state_plot_type, year_value)
    return fig

if __name__ == '__main__':
    app.run_server(debug=DEBUG)
