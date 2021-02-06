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

DEBUG = True

external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

if not DEBUG:
    server = app.server

app.layout = html.Div(children = [
    html.H1("Hello world!")
])

if __name__ == '__main__':
    app.run_server(debug=DEBUG)
