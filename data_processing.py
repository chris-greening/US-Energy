import csv
import datetime

import pandas as pd

def map_from_csv(fpath: str, drop_header=True) -> dict:
    with open(fpath, mode='r') as infile:
        reader = csv.reader(infile)
        if drop_header:
            next(reader, None)
        return {rows[0]: rows[1] for rows in reader}

def create_code_columns(df) -> pd.DataFrame:
    df["Energy_code"] = df["MSN"].str[0:2]
    df["Sector_code"] = df["MSN"].str[2:4]
    df["Unit_code"] = df["MSN"].str[4]
    return df

def _determine_subset_list(arg, default):
    if arg is not None:
        if isinstance(arg, str):
            arg = [arg]
    else:
        arg = default
    return arg

def data_subset(df, states=None, years=None, sectors=None, sources=None) -> pd.DataFrame:
    all_states = df["State"].unique()
    all_years = df["Year"].unique()
    all_sectors = df["Sector"].unique()
    all_sources = df["Source"].unique()

    states = _determine_subset_list(states, all_states)
    years = _determine_subset_list(years, all_years)
    sectors = _determine_subset_list(sectors, all_sectors)
    sources = _determine_subset_list(sources, all_sources)

    masks = [
        df["State"].isin(states),
        df["Year"].isin(years),
        df["Sector"].isin(sectors),
        df["Source"].isin(sources)
    ]
    final_mask = [all(row) for row in zip(*masks)]

    return df[final_mask]

def load_dataset():
    """Return a DataFrame with all of the mapped data"""
    df = pd.read_csv(os.path.join("data", "use_all_btu.csv"))

    state_abbr_map = map_from_csv(os.path.join("data", "states.csv"))
    energy_codes_map = map_from_csv(os.path.join("data", "energy_codes.csv"))
    sector_codes_map = map_from_csv(os.path.join("data", "sector_codes.csv"))
    unit_codes_map = map_from_csv(os.path.join("data", "unit_codes.csv"))
    # state_color_map = map_from_csv(r"data\state_plot_colors.csv")

    df = create_code_columns(df)
    df.loc[df["Sector_code"] == "ET", "Sector_code"] = "TC"

    df = df.rename(columns={"State": "Abbreviation"})

    # Mapping codes to full values
    df["State"] = df["Abbreviation"].map(state_abbr_map)
    df["Source"] = df["Energy_code"].map(energy_codes_map)
    df["Sector"] = df["Sector_code"].map(sector_codes_map)
    df["Unit"] = df["Unit_code"].map(unit_codes_map)

    # Setting million BTU columns
    per_capita_rows = df["Sector"].str.contains("per capita")
    df.loc[per_capita_rows, "Unit"] = "Million BTU"

    # Remove non-state entities
    # not_states = ["US", "DC"]
    # df = df[~df["Abbreviation"].isin(not_states)]

    # Dropping MSN's that don't end in B (GDP and generation)
    df = df[~df["MSN"].str[-1].isin(["X", "R"])]

    # Filtering out rows that aren't related to consumption
    consumption_codes = ["AC", "CC", "IC", "RC",
                        "TC", "AP", "IP", "CP", "RP", "TP"]

    df = df[df["Sector_code"].isin(consumption_codes)]
    df = df[~df["Energy_code"].isin(["TN", "TP", "P1"])]

    # Remove MSN code names
    df = df.drop(columns=["Data_Status", "MSN", "Abbreviation",
                        "Energy_code", "Sector_code", "Unit_code"])

    id_vars = ["State", "Source", "Sector", "Unit"]
    df = df.melt(id_vars=id_vars, var_name="Year", value_name="BTU")

    df["Year"] = df["Year"].astype(int)

    return df

def load_primary_energy_sources(df):
    df = data_subset(
            df,
            sources=[
                "Renewable energy",
                "Natural gas (excluding supplemental gaseous fuels)",
                "Coal", "Nuclear electric power",
                "All petroleum products - excluding biofuels"
            ]
    )
    df["Source"] = df["Source"].replace(
        {
            "Renewable energy": "Renewables",
            "Natural gas (excluding supplemental gaseous fuels)": "Natural gas",
            "Nuclear electric power": "Nuclear",
            "All petroleum products - excluding biofuels": "Petroleum"
        },
        regex = False
    )
    return df
