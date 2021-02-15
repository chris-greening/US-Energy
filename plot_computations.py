import datetime
import json
import pathlib
import os

import plotly.express as px
import plotly
import plotly.io as pio

import data_processing as dp
import plotting
import presidents

def precompute_main_plots(total_df, primary_df, depiction, x_axis):
    # depiction_types = ["Energy consumption", "Energy consumption (per capita)", "Energy consumption (per resource)", "Resource consumption"]
    # x_axis_types = ["Year", "President"]

    # combinations = [[depiction, x_axis] for depiction in depiction_types for x_axis in x_axis_types]

    # figs = {}
    # for depiction, x_axis in combinations:
    fig = us_total(total_df, primary_df, depiction, x_axis)
    # figs[depiction + x_axis] = fig
    return fig

def us_total(total_df, primary_df, depiction_type, x_axis_type):
    # Subset the data
    per_cap_df = dp.data_subset(total_df, states=["United States"], sectors=["Total consumption per capita"], sources=["Total"])
    consumption_df = dp.data_subset(primary_df, states=["United States"], sectors=["Total"])

    # Prepare the dataset
    consumption_df["BTU"] = consumption_df["BTU"]/1_000_000
    consumption_df = consumption_df.rename(columns={"BTU": "Quadrillion BTU"})
    per_cap_df = per_cap_df.rename(columns={"BTU": "Million BTU"})

    # Determine the marker size
    marker_size = (per_cap_df["Million BTU"] /
                   per_cap_df["Million BTU"].max())**5


    total_df = consumption_df.groupby(["Year"], as_index=False).sum()
    min_x, max_x, min_y, max_y = calculate_bounds(total_df)
    if depiction_type == "Energy consumption":
        fig = px.scatter(
            total_df,
            x="Year",
            y="Quadrillion BTU",
            size=marker_size,
            color=per_cap_df["Million BTU"],
            color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
            hover_name="Year",
            range_x=[min_x, max_x],
            range_y=[min_y, max_y],
            # height=500,
            size_max=12
        )
    elif depiction_type == "Energy consumption (per capita)":
        min_x = datetime.date(1960, 1, 1)
        min_y = per_cap_df["Million BTU"].min()
        min_y = min_y - min_y*.05

        max_x = datetime.date(2018, 1, 1)
        max_y = per_cap_df["Million BTU"].max()
        max_y = max_y + max_y*.05

        fig = px.scatter(
            per_cap_df,
            x="Year",
            y="Million BTU",
            hover_name="Year",
            size=marker_size,
            color=per_cap_df["Million BTU"],
            color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
            range_x=[min_x, max_x],
            range_y=[min_y, max_y],
            size_max=12
        )
    elif depiction_type == "Energy consumption (per resource)":
        total_resource_df = consumption_df.groupby(["Year", "Source"], as_index=False).sum()
        min_y = 0
        fig = px.area(
            total_resource_df,
            x="Year",
            y="Quadrillion BTU",
            color="Source",
            color_discrete_map=plotting.ENERGY_SOURCE_COLORS,
            range_x=[min_x, max_x],
            range_y=[min_y, max_y]
        )
    else:
        resource_df = consumption_df.groupby(
            ["Year", "Source"], as_index=False).sum()
        min_x, max_x, min_y, max_y = calculate_bounds(resource_df)
        fig = px.line(
            resource_df,
            x="Year",
            y="Quadrillion BTU",
            color="Source",
            color_discrete_map=plotting.ENERGY_SOURCE_COLORS,
            range_x=[min_x, max_x],
            range_y=[min_y, max_y]
        )

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=58,
                        label="1960",
                        step="year",
                        stepmode="backward"),
                    dict(count=48,
                        label="1970",
                        step="year",
                        stepmode="backward"),
                    dict(count=38,
                        label="1980",
                        step="year",
                        stepmode="backward"),
                    dict(count=28,
                        label="1990",
                        step="year",
                        stepmode="backward"),
                    dict(count=18,
                        label="2000",
                        step="year",
                        stepmode="backward"),
                    dict(count=8,
                        label="2010",
                        step="year",
                        stepmode="backward"),
                ])
            ),
            type="date"
        )
    )
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    fig.update_layout(hovermode="x")
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Million BTU per capita",
        )
    )
    if x_axis_type == "President":
        add_presidential_axes(fig)

    fig.update_layout(plotting.PLOT_COLORS)
    return fig

def calculate_bounds(consumption_df):
    min_x = datetime.date(1960, 1, 1)
    min_y = consumption_df["Quadrillion BTU"].min()
    min_y = min_y - min_y*.05

    max_x = datetime.date(2018, 1, 1)
    max_y = consumption_df["Quadrillion BTU"].max()
    max_y = max_y + max_y*.05

    return min_x, max_x, min_y, max_y

def add_presidential_axes(fig) -> None:
    fig.add_vrect(
        x0="1960-01-01", x1="1961-01-01",
        fillcolor=plotting.PRESIDENTIAL_PARTY_COLORS["Republican"], opacity=0.5,
        layer="below", line_width=.5,
    )

    ticktext = []
    tickvals = []
    for president in presidents.presidents:
        fig.add_vrect(
            x0=president.start,
            x1=president.end,
            fillcolor=plotting.PRESIDENTIAL_PARTY_COLORS[president.party],
            opacity=0.5,
            layer="below",
            line_width=0.5
        )
        ticktext.append(president.name)
        tickvals.append(president.start)
    fig.update_xaxes(showgrid=False, ticktext=ticktext, tickvals=tickvals, title="President")
    fig.update_yaxes(showgrid=False)

def us_primary_per_year(primary_df, year):
    consumption_df = dp.data_subset(primary_df, states=["United States"], sectors=["Total"])
    consumption_df = consumption_df.groupby(["Year", "Sector", "Source"], as_index=False).sum()
    consumption_df["BTU"] = consumption_df["BTU"]/1_000_000
    consumption_df = consumption_df.rename(columns={"BTU": "Quadrillion BTU"})

    min_y = 0
    max_y = consumption_df["Quadrillion BTU"].max()
    max_y = max_y + max_y*.05

    fig = px.bar(
            consumption_df[consumption_df["Year"] == year],
            x="Source",
            y="Quadrillion BTU",
            color="Source",
            range_y=[min_y, max_y],
            color_discrete_map=plotting.ENERGY_SOURCE_COLORS
    )
    fig.update_layout(plotting.PLOT_COLORS, showlegend=False)
    fig.update_xaxes(title_text="", categoryorder="total ascending")
    return fig

def precompute_state_per_year(total_df, primary_df, depiction, year):

    # Prepare the datasets
    # primary_df = dp.load_primary_energy_sources(total_df)
    primary_df = dp.data_subset(primary_df, states=[state for state in total_df["State"].unique(
    ) if state != "United States"], sectors=["Total"])
    primary_df["BTU"] = primary_df["BTU"]/1_000_000
    primary_df = primary_df.rename(columns={"BTU": "Quadrillion BTU"})

    per_cap_df = dp.data_subset(total_df, states=[state for state in total_df["State"].unique(
    ) if state != "United States"], sources=["Total"], sectors=["Total consumption per capita"])
    per_cap_df = per_cap_df.rename(columns={"BTU": "Million BTU"})

    max_y = primary_df.groupby(["State", "Year"]).sum()["Quadrillion BTU"].max()
    per_cap_max_y = per_cap_df.groupby(["State", "Year"]).sum()["Million BTU"].max()
    max_y = max_y + max_y*.05

    # Create all possible combinations of plots
    # depiction_types = ["Energy consumption", "Energy consumption (per capita)"]
    # years = total_df["Year"].unique()
    # combinations = [[depiction, year]
    #                 for depiction in depiction_types for year in years]

    # figs = {}
    # for depiction, year in combinations:
    if depiction == "Energy consumption":
        year_df = primary_df[primary_df["Year"] == year]
        year_df = year_df.groupby("State", as_index=False).sum()
        fig = state_bar_plot(year_df, max_y)
    else:
        year_df = per_cap_df[per_cap_df["Year"] == year]
        fig = state_per_cap_bar_plot(year_df, per_cap_max_y)
        # figs[depiction+str(year)] = fig
    return fig

def state_bar_plot(primary_df, max_y):
    # Prepare the dataset

    min_y = 0

    fig = px.bar(
        primary_df,
        x="State",
        y="Quadrillion BTU",
        # color="Source",
        range_y=[min_y, max_y],
        color_discrete_map=plotting.ENERGY_SOURCE_COLORS
    )
    fig.update_xaxes(title_text="", categoryorder="total ascending", tickfont=dict(size=8), tickmode="linear")
    fig.update_layout(plotting.PLOT_COLORS, showlegend=False)
    return fig

def state_per_cap_bar_plot(per_cap_df, max_y):
    min_y = 0

    fig = px.bar(
        per_cap_df,
        x="State",
        y="Million BTU",
        color="Million BTU",
        color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
        range_y=[min_y, max_y],
        range_color=[0, max_y]
    )
    fig.update_xaxes(title_text="", categoryorder="total ascending",
                     tickfont=dict(size=8), tickmode="linear")
    fig.update_layout(plotting.PLOT_COLORS, showlegend=False)
    return fig

def pie_plot_per_year(primary_df, year):
    consumption_df = dp.data_subset(primary_df, states=["United States"], sectors=["Total"])
    consumption_df = consumption_df.groupby(["Year", "Sector", "Source"], as_index=False).sum()
    consumption_df["BTU"] = consumption_df["BTU"]/1_000_000
    consumption_df = consumption_df.rename(columns={"BTU": "Quadrillion BTU"})

    fig = px.pie(
            consumption_df[consumption_df["Year"] == year],
            names="Source",
            values="Quadrillion BTU",
            color="Source",
            color_discrete_map=plotting.ENERGY_SOURCE_COLORS,
            hole=.4
    )
    fig.update_layout(plotting.PLOT_COLORS)
    return fig

def update_choropleth(df, geojson):
    # Prepare the datasets
    primary_df = dp.load_primary_energy_sources(df)
    primary_df = dp.data_subset(primary_df, states=[state for state in primary_df["State"].unique(
    ) if state != "United States"], sectors=["Total"])
    primary_df["BTU"] = primary_df["BTU"]/1_000_000
    primary_df = primary_df.rename(columns={"BTU": "Quadrillion BTU"})
    primary_df = primary_df.groupby(["State", "Year"], as_index=False).sum()
    primary_df = primary_df[primary_df["Year"] == 2018]

    per_cap_df = dp.data_subset(df, states=[state for state in df["State"].unique(
    ) if state != "United States"], sources=["Total"], sectors=["Total consumption per capita"])
    per_cap_df = per_cap_df.rename(columns={"BTU": "Million BTU per capita"})

    max_y = per_cap_df["Million BTU per capita"].max()

    fig = px.choropleth_mapbox(
                            per_cap_df,
                            geojson=geojson,
                            locations="State",
                            color="Million BTU per capita",
                            featureidkey="properties.NAME",
                            color_continuous_scale=plotly.colors.diverging.Temps,
                            range_color=(0, max_y),
                            animation_frame="Year",
    )
    fig.update_layout(
                mapbox_style="carto-positron",
                mapbox_zoom=2.2,
                mapbox_center={"lat": 37.8, "lon": -95.7},
    )
    fig.update_layout(plotting.CHOROPLETH_COLORS)
    # fig.update_layout(plotting.CHOROPLETH_COLORS)
    return fig
