import datetime

import plotly.express as px
import plotly

import data_processing as dp
import plotting

def us_total(total_df, primary_df):
    # Subset the data
    per_cap_df = dp.data_subset(total_df, states=["United States"], sectors=["Total consumption per capita"], sources=["Total"])
    consumption_df = dp.data_subset(primary_df, states=["United States"], sectors=["Total"])

    # Prepare the dataset
    consumption_df = consumption_df.groupby(["Year"], as_index=False).sum()
    consumption_df["BTU"] = consumption_df["BTU"]/1_000_000
    consumption_df = consumption_df.rename(columns={"BTU": "Quadrillion BTU"})
    per_cap_df = per_cap_df.rename(columns={"BTU": "Million BTU"})

    # Determine the marker size
    marker_size = (per_cap_df["Million BTU"] /
                   per_cap_df["Million BTU"].max())**5

    fig = px.scatter(
        consumption_df,
        x="Year",
        y="Quadrillion BTU",
        size=marker_size,
        color=per_cap_df["Million BTU"],
        color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
        hover_name="Year",
        range_x=[datetime.date(1960, 1, 1), datetime.date(2018, 1, 1)],
        height=500,
        size_max=12
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
    fig.update_layout(plotting.PLOT_COLORS)
    return fig

    # return per_cap_df, consumption_df

def us_total_stacked_area(primary_df):
    consumption_df = dp.data_subset(primary_df, states=["United States"], sectors=["Total"])
    consumption_df = consumption_df.groupby(["Year", "Source"], as_index=False).sum()
    consumption_df = consumption_df.rename(columns={"BTU": "Quadrillion BTU"})
    fig = px.area(consumption_df, x="Year", y="Quadrillion BTU", color="Source",
                  color_discrete_map=plotting.ENERGY_SOURCE_COLORS)
    return fig

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
