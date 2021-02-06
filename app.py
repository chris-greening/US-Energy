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
                                html.H3("Energy consumption"),
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
                                html.H3(id="us-primary-header"),
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
            )
        ],
        className="container-fluid dash"
    )
])


########## HEADERS
@app.callback(
    Output('us-primary-header', 'children'),
    Input('us-total', 'hoverData')
)
def us_primary_bar(hoverData):
    year_value = int(hoverData['points'][0]['x'][:4])
    return f"Energy consumption ({year_value})"

########## BAR PLOT

@app.callback(
    Output('us-primary-bar', 'figure'),
    Input('us-total', 'hoverData')
)
def us_primary_bar(hoverData):
    year_value = int(hoverData['points'][0]['x'][:4])
    fig = us_primary_bar_dict[year_value]
    return fig

if __name__ == '__main__':
    app.run_server(debug=DEBUG)
