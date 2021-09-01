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
import pandas as pd
import datetime as dt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

pd.options.plotting.backend = "plotly"


def exceed(df):
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


def univar_monstats(df, varnm, display=True):
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


def bivar_stats(df, steph=0.5, stept=1):
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
    if not all(
        [any(df.columns == "hs"), any(df.columns == "t0m1"), any(df.columns == "cge")]
    ):
        raise NameError("Crucial parameter missing: " "hs" "," "t0m1" " or " "cge" "")
    else:
        hsbin = steph * np.arange(
            np.floor(df["hs"].min() / steph), 1 + np.ceil(df["hs"].max() / steph)
        )
        tebin = stept * np.arange(
            np.floor(df["t0m1"].min() / stept), 1 + np.ceil(df["t0m1"].max() / stept)
        )
        tabprc = np.zeros([len(hsbin), len(tebin)])
        tabcnt = np.zeros([len(hsbin), len(tebin)])
        tabcgemn = np.zeros([len(hsbin), len(tebin)])
        tabcgesd = np.zeros([len(hsbin), len(tebin)])
        hsnm = []
        tenm = []
        for idy, hsl in enumerate(hsbin):
            for idx, tel in enumerate(tebin):
                if idx == 1:
                    hsnm.append(str(pd.Interval(left=hsl, right=hsl + steph)))
                if idy == 1:
                    tenm.append(str(pd.Interval(left=tel, right=tel + stept)))
                cgesub = (
                    df["cge"]
                    .loc[
                        (df["hs"] > hsl)
                        & (df["hs"] <= (hsl + steph))
                        & (df["t0m1"] > tel)
                        & (df["t0m1"] <= (tel + stept))
                    ]
                    .values
                )
                if not cgesub.size == 0:
                    tabprc[idy, idx] = 100 * len(cgesub) / len(df)
                    tabcnt[idy, idx] = len(cgesub)
                    tabcgemn[idy, idx] = cgesub.mean()
                    tabcgesd[idy, idx] = cgesub.std()
        dfprc = pd.DataFrame(data=tabprc, columns=tenm, index=hsnm)
        dfcnt = pd.DataFrame(data=tabcnt, columns=tenm, index=hsnm)
        dfcgemn = pd.DataFrame(data=tabcgemn, columns=tenm, index=hsnm)
        dfcgesd = pd.DataFrame(data=tabcgesd, columns=tenm, index=hsnm)
        return dfprc, dfcnt, dfcgemn, dfcgesd


def disp_table(df, title):
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


def bivar_monstats(df, filename="resource_assess", steph=0.5, stept=1, disptab=True):
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
    if filename[-4:] == ".csv":
        filename = filename[:-4]

    moun = df.index.month.unique()
    tallprc, tallcnt, tallcgemn, tallcgesd = bivar_stats(df, steph=0.5, stept=1)
    tallprc.to_csv(
        filename + "_All_perc_occur.csv",
        index=True,
        index_label="Hs/Te",
        header=True,
        float_format="%.1f",
    )
    tallcnt.to_csv(
        filename + "_All_count.csv",
        index=True,
        index_label="Hs/Te",
        header=True,
        float_format="%.1f",
    )
    tallcgemn.to_csv(
        filename + "_All_av_energy_flux.csv",
        index=True,
        index_label="Hs/Te",
        header=True,
        float_format="%.1f",
    )
    tallcgesd.to_csv(
        filename + "_All_std_energy_flux.csv",
        index=True,
        index_label="Hs/Te",
        header=True,
        float_format="%.1f",
    )
    if disptab:
        disp_table(tallprc, "Percentage Occurence - All")
        disp_table(tallcnt, "Number Occurence - All")
        disp_table(tallcgemn, "Average Energy Flux - All")
        disp_table(tallcgesd, "Energy Flux ST. Dev - All")
    for mo in moun:
        subs = df[df.index.month == mo]
        tmprc, tmcnt, tmcgemn, tmcgesd = bivar_stats(subs)
        monm = dt.datetime(2000, mo, 1).strftime("%b")
        tmprc.to_csv(
            filename + "_" + monm + "_perc_occur.csv",
            index=True,
            index_label="Hs/Te",
            header=True,
            float_format="%.1f",
        )
        tmcnt.to_csv(
            filename + "_" + monm + "_count.csv",
            index=True,
            index_label="Hs/Te",
            header=True,
            float_format="%.1f",
        )
        tmcgemn.to_csv(
            filename + "_" + monm + "_av_energy_flux.csv",
            index=True,
            index_label="Hs/Te",
            header=True,
            float_format="%.1f",
        )
        tmcgesd.to_csv(
            filename + "_" + monm + "_std_energy_flux.csv",
            index=True,
            index_label="Hs/Te",
            header=True,
            float_format="%.1f",
        )
        if disptab:
            disp_table(tmprc, "Percentage Occurence - " + monm)
            disp_table(tmcnt, "Number Occurence - " + monm)
            disp_table(tmcgemn, "Average Energy Flux - " + monm)
            disp_table(tmcgesd, "Energy Flux ST. Dev - " + monm)