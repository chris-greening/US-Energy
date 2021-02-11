import datetime

import plotly.express as px
import plotly

import data_processing as dp
import plotting
import presidents

def precompute_main_plots(total_df, primary_df):
    depiction_types = ["Total", "Total (by resource)", "Resource"]
    x_axis_types = ["Year", "President"]

    combinations = [[depiction, x_axis] for depiction in depiction_types for x_axis in x_axis_types]

    figs = {}
    for depiction, x_axis in combinations:
        fig = us_total(total_df, primary_df, depiction, x_axis)
        figs[depiction + x_axis] = fig
    return figs

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


    if depiction_type == "Total":
        consumption_df = consumption_df.groupby(["Year"], as_index=False).sum()
        min_x, max_x, min_y, max_y = calculate_bounds(consumption_df)
        fig = px.scatter(
            consumption_df,
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
    elif depiction_type == "Total (by resource)":
        min_x, max_x, min_y, max_y = calculate_bounds(consumption_df)
        consumption_df = consumption_df.groupby(["Year", "Source"], as_index=False).sum()
        fig = px.area(
            consumption_df,
            x="Year",
            y="Quadrillion BTU",
            color="Source",
            color_discrete_map=plotting.ENERGY_SOURCE_COLORS,
            range_x=[min_x, max_x],
            range_y=[min_y, max_y]
        )
    else:
        consumption_df = consumption_df.groupby(
            ["Year", "Source"], as_index=False).sum()
        min_x, max_x, min_y, max_y = calculate_bounds(consumption_df)
        fig = px.line(
            consumption_df,
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

    # return per_cap_df, consumption_df

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
    fig.update_xaxes(showgrid=False, ticktext=ticktext, tickvals=tickvals)
    fig.update_yaxes(showgrid=False)

def us_primary_per_year(primary_df):
    consumption_df = dp.data_subset(primary_df, states=["United States"], sectors=["Total"])
    consumption_df = consumption_df.groupby(["Year", "Sector", "Source"], as_index=False).sum()
    consumption_df["BTU"] = consumption_df["BTU"]/1_000_000
    consumption_df = consumption_df.rename(columns={"BTU": "Quadrillion BTU"})

    min_y = 0
    max_y = consumption_df["Quadrillion BTU"].max()
    max_y = max_y + max_y*.05

    figs = {}
    for year in consumption_df["Year"].unique():
        fig = px.bar(
                consumption_df[consumption_df["Year"] == year],
                x="Source",
                y="Quadrillion BTU",
                color="Source",
                range_y=[min_y, max_y],
                color_discrete_map=plotting.ENERGY_SOURCE_COLORS
        )
        fig.update_layout(plotting.PLOT_COLORS)
        fig.update_xaxes(title_text="", categoryorder="total ascending")
        figs[year] = fig
    return figs

def us_primary_per_year_pie(primary_df):
    consumption_df = dp.data_subset(
        primary_df, states=["United States"], sectors=["Total"])
    consumption_df = consumption_df.groupby(
        ["Year", "Sector", "Source"], as_index=False).sum()
    consumption_df["BTU"] = consumption_df["BTU"]/1_000_000
    consumption_df = consumption_df.rename(columns={"BTU": "Quadrillion BTU"})

    figs = {}
    for year in consumption_df["Year"].unique():
        fig = px.pie(
            consumption_df[consumption_df["Year"] == year],
            values="Quadrillion BTU",
            names="Source",
            color="Source",
            color_discrete_map=plotting.ENERGY_SOURCE_COLORS
        )
        fig.update_layout(plotting.PLOT_COLORS)
        figs[year] = fig
    return figs
