# -*- coding: utf-8 -*-
"""
Resource Assessment module

The module allows calculation and production of some of the standard
deliverables for resource assessment listed in IEC 62600-101 for
reconnoicanse and feasibility study.
The calculations are based on energy flux, significant wave height and
energy period parameters from RCODE database. The module produces univariate
statistics for energy flux, bi-variate statistics and energy values binned in
significant wave height and energy period

IMPORTANT: read_data_temp - is a temporary method to be replaced by method to
export the data directly from Casandra

Created on Wed Dec  2 14:14:48 2020
@author: david.darbinyan
"""
from pathlib import Path
import pandas as pd
import datetime as dt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

pd.options.plotting.backend = "plotly"


def exceed(df: pd.DataFrame):
    """
    Returns ranked data and exceedance probabilities

    Parameters
    ----------
    df : PANDAS DATAFRAME
        Dataframe that contains either full data or subset (yearly or monthly)
        in a format consistent with RCODE data extraction

    Returns
    -------
    datasrt : PANDAS DATAFRAME
        Input dataframe sorted in ascending order
    exceedance : NUMPY ARRAY
        Calculated exceedance probabilities for the ranked input data
    """
    datasrt = df.sort_values(ascending=False)
    exceedance = np.linspace(0, 1, len(datasrt), endpoint=False)[::-1]
    return datasrt, exceedance


def univar_monstats(df: pd.DataFrame, varnm: str, display: bool = True):
    """
    Method to calculate univariate statistics for any input variable. Used in
    resource assessment to produce deliverables as per IEC

    The mehtod produces plots including monthly statistcs and yearly statistics
    for the input variable and monthly exceedance plots

    Parameters
    ----------
    df : PANDAS DATAFRAME
        Dataframe containing the data.
    varnm : STRING
        Variable name as in dataframe column names
    display : BOOLEAN
        Graphic has to be displayed. Default to False

    Returns
    -------
    dty : PANDAS DATAFRAME
        Contains yearly statistics for the chosen variable.
    dtm : PANDAS DATAFRAME
        Contains monthly statistics for the chosen variable.
    """
    if varnm not in df.columns:
        existing_col = ", ".join(sorted(df.columns))
        raise NameError(
            f"Parameter {varnm} is not in the dataframe. "
            f"Possible values are: {existing_col}"
        )
    # sort rows according to the variable selected
    sorted_df = df[[varnm]].sort_values(by=varnm)

    # Extract some time information
    sorted_df["month_index"] = sorted_df.index.month
    sorted_df["month"] = sorted_df.index.month_name()
    sorted_df["year"] = sorted_df.index.year

    if display:
        # Compute the percentile of rows inside each group (pct == percentage).
        sorted_df["Exceedance"] = sorted_df.groupby("month")[varnm].rank(
            method="min", pct=True
        )
        sorted_df.plot.line(x=varnm, y="Exceedance", color="month", line_group="month")

    res = []

    # For month, groups on month_index (number) and month (name) to keep month order
    for groups in (["month_index", "month"], ["year"]):
        # describe get mean, min, max, stdev, 25%, 50% and 75% and count
        dtm = sorted_df.groupby(groups)[varnm].describe()
        # reset_index to get index as column (e.g. month and month_index )
        dtm = dtm.reset_index()
        res.append(dtm)

        if display:
            fig = px.line(dtm, x=dtm[groups[-1]], y=["mean", "max", "min"])

            fig.add_trace(
                go.Scatter(
                    x=dtm[groups[-1]],
                    y=dtm["mean"] + dtm["std"],
                    line=dict(color="rgba(0,0,0,0)"),
                    showlegend=False,
                    text="mean + stdev",
                    name="",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=dtm[groups[-1]],
                    y=dtm["mean"] - dtm["std"],
                    fill="tonexty",
                    line=dict(color="rgba(0,0,0,0)"),
                    fillcolor="rgba(142,186,217,0.5)",
                    opacity=0.5,
                    name="St.dev",
                    text="mean-stdev",
                )
            )
            fig.update_layout(yaxis_title=varnm)

            # We have all the x index already (don't use float number for year)
            fig.update_xaxes(type="category")
            fig.show()
    return res


def bivar_stats(df: pd.DataFrame, steph: float = 0.5, stept: float = 1):
    """
    Method to calculate bi-variate statistcs and average and standard deviation
    of energy flux binned in significant wave height and energy period bins.

    Produces dataframes containing percentage occurrence, number occurrence,
    average energy flux and energy flux standard devaition for significant
    wave height vs energy period tables

    Parameters
    ----------
    df : PANDAS DATAFRAME
        Dataframe containing input data
    steph : DOUBLE, optional
        Bin size for significant wave height. The default is 0.5.
    stept : DOUBLE, optional
        Bin size for energy period. The default is 1.

    Raises
    ------
    NameError
        The input dataframe should contain the following columns: 'hs','t0m1'
        and 'cge'

    Returns
    -------
    dfprc : PANDAS DATAFRAME
        Dataframe containing percentage occurrence for significant wave
        height (hs) vs energy period (t0m1). Indices are hs bins, columns
        are t0m1 bins
    dfcnt : PANDAS DATAFRAME
        Dataframe containing number occurrence for significant wave
        height (hs) vs energy period (t0m1). Indices are hs bins, columns
        are t0m1 bins
    dfcgemn : PANDAS DATAFRAME
        Dataframe containing average energy flux for significant wave
        height (hs) vs energy period (t0m1) bins. Indices are hs bins, columns
        are t0m1 bins
    dfcgesd : PANDAS DATAFRAME
        Dataframe containing st deviation of energy flux for significant wave
        height (hs) vs energy period (t0m1) bins. Indices are hs bins, columns
        are t0m1 bins

    """

    required_columns = {"hs", "cge", "t0m1"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing_params = ", ".join(sorted(missing_columns))
        raise NameError(f"Crucial parameter missing: {missing_params}")

    # upperbound (end) has to be greater than max as it is excluded
    # XX: Having end = max + freq should be enough but fails in the test
    hsbin = pd.interval_range(
        start=np.floor(df["hs"].min()),
        end=df["hs"].max() + 2 * steph,
        freq=steph,
        name="hs",
    )
    tebin = pd.interval_range(
        start=np.floor(df["t0m1"].min()),
        end=df["t0m1"].max() + 2 * stept,
        freq=stept,
        name="tebin",
    )

    # Add a column indicating the containing interval
    df = df.assign(hsbin=pd.cut(df.hs, bins=hsbin), tebin=pd.cut(df.t0m1, bins=tebin))

    # For ddof (Delta Degrees of Freedom) see:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.std.html
    # The rationnal is:
    # - in numpy ddof is 0 by default
    # - in pandas ddof is 1 by default
    stats = df.groupby(by=["hsbin", "tebin"]).agg(
        count=("cge", "count"),
        mean=("cge", np.mean),
        stdev=("cge", lambda x: np.std(x, ddof=0)),
    )
    stats["percentage"] = 100 * stats["count"] / len(df)

    # Groupby create a hierarchical index (hsbin and tebin)
    # It pivots the last level of index and put it as column.
    # res has:
    # - hsbin as row index
    # - MultiIndex([count, mean, stdev, percentage], tebin) as column index
    res = stats.unstack(level=-1)

    # default value for mean, count, percentage and stdev is 0
    res = res.fillna(0)
    return (
        res["percentage"],
        res["count"],
        res["mean"],
        res["stdev"],
    )


def disp_table(df: pd.DataFrame, title: str):
    """
    Method to output tables - (courtesy of Chris Old, Edinburgh University)
    Parameters
    ----------
    store : TYPE
        DESCRIPTION.
    mVarName : TYPE
        DESCRIPTION.
    Returns
    -------
    None.
    """
    pd.set_option(
        "display.float_format",
        "{:3,.3f}".format,
        "display.max_columns",
        None,
        "display.max_rows",
        None,
    )
    print(title, "\n")
    print(df)


def bivar_monstats(
    df: pd.DataFrame,
    filename: str = "resource_assess",
    steph: float = 0.5,
    stept: float = 1,
    disptab: bool = True,
):
    """
    Method to produce monthly and annual bi-variate statistics and energy flux
    tables. These are calculated from bivar_stats method in a loop and saved
    as csv file

    Parameters
    ----------
    df : PANDAS DATAFRAME
        Input data in RCODE dataframe format.
    filename : STR, optional
        Full path to output file name, results will have suffix added
        describing the time period and type of the produced table.
        The default is 'resource_assess'.
    steph : DOUBLE, optional
        Bin size for significant wave height. The default is 0.5.
    stept : DOUBLE, optional
        Bin size for energy period. The default is 1.

    Returns
    -------
    None. Writes csv files.

    """
    # with_suffix put an empty string as suffix (thus removing potential suffix)
    base_path = Path(filename).with_suffix("")

    def write_and_display_dataframe(
        df: pd.DataFrame, file_path: str, title: str, display: bool
    ):
        df.to_csv(
            file_path,
            index=True,
            index_label="Hs/Te",
            header=True,
            float_format="%.1f",
        )
        if display:
            disp_table(df, title)

    moun = df.index.month.unique()
    all_stat = bivar_stats(df, steph=steph, stept=stept)

    filenames = [
        f"{base_path}_{name}"
        for name in (
            "All_perc_occur.csv",
            "All_count.csv",
            "All_av_energy_flux.csv",
            "All_std_energy_flux.csv",
        )
    ]
    titles = [
        "Percentage Occurence - All",
        "Number Occurence - All",
        "Average Energy Flux - All",
        "Energy Flux ST. Dev - All",
    ]
    for stat, filename, title in zip(all_stat, filenames, titles):
        write_and_display_dataframe(stat, filename, title, disptab)

    for mo in moun:
        subs = df[df.index.month == mo]
        monthly_stats = bivar_stats(subs, steph=steph, stept=stept)
        monm = dt.datetime(2000, mo, 1).strftime("%b")
        filenames = [
            f"{base_path}_{monm}_{name}_"
            for name in (
                "perc_occur.csv",
                "count.csv",
                "av_energy_flux.csv",
                "std_energy_flux.csv",
            )
        ]
        titles = [
            f"Percentage Occurence - {monm}",
            f"Number Occurence - {monm}",
            f"Average Energy Flux - {monm}",
            f"Energy Flux ST. Dev - {monm}",
        ]
        for stat, filename, title in zip(monthly_stats, filenames, titles):
            write_and_display_dataframe(stat, filename, title, disptab)
