#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import configparser
import logging
from pathlib import Path

import numpy as np
from numpy import triu_indices, tril_indices

CONFIG_FILEPATHS = [
    os.environ.get("RESOURCECODE_CONFIG_FILEPATH"),
    "./resourcecode.ini",
    "~/.config/resourcecode.ini",
    f"{sys.prefix}/etc/resourcecode/config.ini",
]

LOGGER = logging.getLogger("resourcecode.default")
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(os.environ.get("RESOURCECODE_LOG_THRESHOLD", "WARNING"))


def get_config():
    config = configparser.ConfigParser()
    for config_filepath in CONFIG_FILEPATHS:
        LOGGER.debug("try reading config from %s", config_filepath)
        if not config_filepath:
            continue

        config_filepath = Path(config_filepath).expanduser()
        if not config_filepath.exists():
            continue

        config.read(config_filepath)
        LOGGER.info("config loaded from %s", config_filepath)
        break
    else:
        raise FileNotFoundError("no config file was found")
    return config


def set_trig(m, values, part="upper"):
    """Set the `values` upper/lower `part` of the square matrix `m`"""
    part = part.lower()
    if part == "upper":
        tri_indices = triu_indices(len(values), k=1)
    elif part == "lower":
        tri_indices = tril_indices(len(values), k=-1)
    else:
        raise ValueError(f"part must be 'lower' or 'upper', '{part}' given")

    for n, (i, j) in enumerate(zip(*tri_indices)):
        m[i, j] = values[n]


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    EARTH_RADIUS_METER = 6367e3
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2

    c = 2 * np.arcsin(np.sqrt(a))
    return c * EARTH_RADIUS_METER
