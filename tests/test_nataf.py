#!/usr/bin/env python3
# coding: utf-8

import pytest
import numpy as np
import pandas as pd

from resourcecode.nataf.censgaussfit import censgaussfit
from resourcecode.nataf.huseby import huseby
from resourcecode.nataf.extrema import get_gpd_parameters

from . import DATA_DIR


def test_censgaussfit_acceptance():
    """this acceptance test assert that the output of the python function is
    the same as the R function, for the same input"""

    quant = 0.9
    X = np.loadtxt(
        DATA_DIR / "censgaussfit" / "input_0.csv",
        usecols=(1, 2, 3),
        delimiter=",",
        skiprows=1,
    )

    data = censgaussfit(X, quant)
    expected = np.loadtxt(
        DATA_DIR / "censgaussfit" / "output_0.csv",
        usecols=(1,),
        delimiter=",",
        skiprows=1,
    )
    assert data.success is True
    assert data.x == pytest.approx(expected, rel=1e-3)


def test_gpd_paramaters():
    """this acceptance test assert that the output of the python function is
    the same as the R function, for the same input"""

    quant = 0.9
    X = pd.read_csv(
        DATA_DIR / "censgaussfit" / "input_0.csv",
        usecols=(1, 2, 3),
        delimiter=",",
    )

    # for the get_gpd_parameters, X must be a dataframe and the index must be a
    # datetime index.  in practise this will not be an issue, has its measure
    # will be attached to a datetime.
    X.index = pd.date_range("2021-01-01", "2021-01-31", len(X))

    expected_parameters = np.array(
        [
            [1.523228, 0.9130694, 0.00566742],
            [2.996940, 1.3203699, 0.24820895],
            [2.187176, 1.2945546, -0.04095130],
        ]
    )

    gpg_parameters = get_gpd_parameters(X, quant)

    # first column is the quantiles, it should be the same as R
    assert gpg_parameters[:, 0] == pytest.approx(expected_parameters[:, 0])

    # second and third column may be more different, but that should be ok
    assert gpg_parameters[:, 1:] == pytest.approx(expected_parameters[:, 1:], abs=1e-1)


def test_nataf_acceptance():
    """this acceptance test assert that the output of the python function is
    the same as the R function, for the same input"""

    pytest.skip("How to test this, knowing it generates random values ?")


def test_huseby_acceptance_3D():
    """this acceptance test assert that the output of the python function is
    the same as the R function, for the same input.

        The input is generated by the `nataf_sim` R function.
        The output is generated by the `huseby` R function.
    """

    ntheta = 120

    simulation = np.loadtxt(
        DATA_DIR / "huseby" / "input_0.csv",
        delimiter=",",
        usecols=(1, 2, 3),
        skiprows=1,
    )

    expected = np.loadtxt(
        DATA_DIR / "huseby" / "output_0.csv",
        delimiter=",",
        usecols=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
        skiprows=1,
    )

    X_expected = expected[:, :3]
    Y_expected = expected[:, 3:6]
    Z_expected = expected[:, 6:9]
    theta_expected = expected[:ntheta, 9]

    X, Y, Z, theta = huseby(simulation, np.array([0.9, 0.95, 0.975]), ntheta=ntheta)

    assert X == pytest.approx(X_expected)
    assert Y == pytest.approx(Y_expected)
    assert Z == pytest.approx(Z_expected)
    assert theta == pytest.approx(theta_expected)


def test_huseby_acceptance_2D():
    """this acceptance test assert that the output of the python function is
    the same as the R function, for the same input.

        The input is generated by the `nataf_sim` R function.
        The output is generated by the `huseby` R function.
    """

    ntheta = 120

    simulation = np.loadtxt(
        DATA_DIR / "huseby" / "input_0.csv",
        delimiter=",",
        usecols=(1, 2),
        skiprows=1,
    )

    expected = np.loadtxt(
        DATA_DIR / "huseby" / "output_1.csv",
        delimiter=",",
        usecols=(1, 2, 3, 4, 5),
        skiprows=1,
    )

    X_expected = expected[:, :2]
    Y_expected = expected[:, 2:4]
    theta_expected = expected[:ntheta, 4]

    X, Y, theta = huseby(simulation, np.array([0.9, 0.95]), ntheta=ntheta)

    assert X == pytest.approx(X_expected)
    assert Y == pytest.approx(Y_expected)
    assert theta == pytest.approx(theta_expected)
