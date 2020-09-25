#!/usr/bin/env python3
# coding: utf-8

from urllib.parse import urljoin
import json

import requests
import pandas as pd
import numpy as np

from resourcecode.utils import get_config


class Client:
    def __init__(self):
        self.config = get_config()

    @property
    def cassandra_base_url(self):
        return self.config.get("default", "cassandra-base-url")

    def get_dataframe_from_criteria(self, criteria):
        """return the pandas dataframe of the data described by the criteria

        Parameters
        ----------
        criteria: string (json)
            a json-formatted string describing the criteria

        Result
        ------
        data: a Pandas DataFrame of the selected data
        """

        parsed_criteria = json.loads(criteria)

        result_array = None
        for parameter in parsed_criteria.get("parameter", ()):
            # we assume that multiple parameters can be given.
            # for each parameter, we make a query and we concatenate all the
            # responses.

            single_parameter_criteria = {
                **parsed_criteria,
                "parameter": [
                    parameter,
                ],
            }
            raw_data = self._get_rawdata_from_criteria(single_parameter_criteria)

            # parameter_array is the time history of the current parameter.
            # it's a 2D array. The first columns is the timestamp, the second
            # one the value of this parameters at the corresponding timestamps.
            parameter_array = np.array(raw_data["result"]["data"])

            try:
                # concatenate and get ride of the timestamp (already known from
                # the previous iteration)
                result_array = np.column_stack((result_array, parameter_array[:, 1]))
            except ValueError:
                result_array = parameter_array

        if result_array is None:
            raise ValueError("no selection parameter found")

        return pd.DataFrame(
            result_array[:, 1:],
            columns=parsed_criteria["parameter"],
            index=pd.to_datetime(result_array[:, 0].astype(int), unit="ms"),
        )

    def _get_rawdata_from_criteria(self, single_parameter_criteria):
        """return the json of the data described by the parameters

        Parameters
        ----------
        parameters: dict
            the dictionnary of parameters to give to cassandra

        Result
        ------
        result: json
            the json result returned by the cassandra database.
        """
        query_url = urljoin(self.cassandra_base_url, "api/timeseries")

        response = requests.get(query_url, single_parameter_criteria)
        if response.ok:
            return response.json()

        raise ValueError(
            "Unable to get a response from the database"
            "(status code = {})".format(response.status_code)
        )
