# Resourcecode library

## Description

The `resourcecode` Marine Data Toolbox is a python package  developed within the  **ResourceCODE** project,
to facilitate the access to a recently developed Metocean hindcast
[database](https://www.umr-lops.fr/Donnees/Vagues/sextant#/metadata/d089a801-c853-49bd-9064-dde5808ff8d8),
and to a set of state-of-the-art methods for data analysis. This toolbox provides developers with a set of standard functions
for resource assessment and operations planning.
The advanced statistical modelling tools provided together with the embedded high resolution wave hindcast database allow the
developers with a set of standard functions for resource assessment, extreme values modelling and operations planning.

It is dedicated to users without the knowledge of manipulating numerous netCDF files or developing statistical analysis,
but is also designed to fulfill expert met-ocean analysts needs. The advanced statistical modelling tools provided allow
the developers of Offshore Renewable Energy (**ORE**) devices to conduct the necessary assessments to reduce uncertainty
in expected environmental conditions,and de-risk investment in future technology design.


## Installation

To install the library, you may first of all, create a dedicated virtual
environment:

```shell
$ cd /your/work/directory
$ python3 -m venv env-resourcecode
```

then, you activate it:

```shell
$ source env-resourcecode/bin/activate
(env-resourcecode)$
```

In this virtual environment, you can now install the library. The library  is
available on PyPI, and installation is straightfoward, using the following
command :

```
(env-resourcecode)$ python -m pip install resourcecode
[…]
```

To test whether the install has been successful, you can run:

```bash
(env-resourcecode)$ python -c "import resourcecode ; print(resourcecode.__version__)"
0.5.5
```

which should print the current locally installed version of `resourcecode`.

## Example of use

Once the library is installed and the configuration is done, you can use the
library.

The first thing to do, is a create a `Client`. The client will query the
cassandra database for you, and return a pandas dataframe of your selection.

See the following example:

```ipython
>>> import resourcecode
>>> client = resourcecode.Client()
>>> data = client.get_dataframe_from_criteria(
"""
{
    "node": 0,
    "start": 1483228400,
    "end": 1489903600,
    "parameter": ["fp", "hs"]
}
""")
>>> data
                        fp     hs
2017-01-01 00:00:00  0.074  0.296
2017-01-01 01:00:00  0.072  0.400
2017-01-01 02:00:00  0.071  0.356
2017-01-01 03:00:00  0.071  0.350
2017-01-01 04:00:00  0.074  0.256
...                    ...    ...
2017-01-31 19:00:00  0.096  0.250
2017-01-31 20:00:00  0.096  0.332
2017-01-31 21:00:00  0.096  0.480
2017-01-31 22:00:00  0.096  0.612
2017-01-31 23:00:00  0.097  0.756

[744 rows x 2 columns]
>>> data.describe()
               fp          hs
count  744.000000  744.000000
mean     0.088046    0.537551
std      0.011400    0.192594
min      0.058000    0.160000
25%      0.081000    0.370000
50%      0.087000    0.533000
75%      0.095000    0.688500
max      0.120000    0.948000

>>> # if you have malptolib installed, you can do the following
>>> ax = data.plot()
>>> ax.figure.savefig('fp_hs.png')
```

which will generate the following plot:

![plot_hs_fp](https://gitlab.ifremer.fr/resourcecode/resourcecode/-/raw/branch/default/fp_hs.png)

## Configuration

The library needs a configuration file to work properly. This file contains in
particular the URL of the Cassandra API to acess the hindcast data.

The library will look for the configuration at the following location (in the
order) :

* in the file described by the `RESOURCECODE_CONFIG_FILEPATH` environment
  variable.
* in a file named `resourcecode.ini` in the current directory.
* in a file located in `$HOME/.config/resourcecode.ini`.
* in a file located in `/usr/local/etc/resourcecode/config.ini`

The search stops at the first file found.

The default configuration file can be found [here](./config/config.ini). You may
download it and move it to this location: `$HOME/.config/resourcecode.ini`.

You may need to update the Cassandra URL.

## Documentation

We recommend starting with the [official documentation](https://resourcecode.gitlab-pages.ifremer.fr/resourcecode/)
of the toolbox.

For examples of the functionalities offered by the toolbox, some Jupyter notebooks are proposed:

 * [Exploratory Data Analysis](https://nbviewer.org/urls/gitlab.ifremer.fr/resourcecode/tools/producible-estimation-showcase/-/raw/branch/default/index.ipynb)
 * [Extreme Values Analysis](https://nbviewer.org/urls/gitlab.ifremer.fr/resourcecode/tools/extreme-values-analysis/-/raw/branch/default/index.ipynb)
 * [Producible estimation](https://nbviewer.org/urls/gitlab.ifremer.fr/resourcecode/tools/producible-estimation-showcase/-/raw/branch/default/index.ipynb)

# Web portal

The `resourcecode`package goes along with a companion [Web Portal](https://resourcecode.ifremer.fr/resources) that allows to see some of its functionalities in action.

Detailed information about the data availibily, tutorials, etc. can be found in the [resources](https://resourcecode.ifremer.fr/resources) page.

Exploration of the hindcast database and some of data exploratory tools are in the [explore](https://resourcecode.ifremer.fr/explore) page.

Both the Jupyter notebook mentioned above and more advanced applications are available as `Jupyter-flex` notebooks. They are
listed on the [Tools](https://resourcecode.ifremer.fr/tools) page.

# Contributing

This package is under active development, and any contribution is welcomed. If you have something
you would like to contribute, but you are not sure how, please don't hesitate to reach out by
sending me an [email](mailto:nicolas.raillard@ifremer.fr) or
opening an [issue](https://gitlab.ifremer.fr/resourcecode/resourcecode/-/issues).

## Citing

Please cite it in your publications and do not hesitate to tell your friends and colleagues about it.

```bibtex
@manual{,
  title = {Resourcecode Toolbox},
  author = {Raillard, Nicolas and Chabot, Simon and Maisondieu, Christophe and Darbynian, David and Payne, Gregory and Papillon, Louis},
  url = {https://gitlab.ifremer.fr/resourcecode/resourcecode},
  year = {2022},
  month = {2},
}
```
## Reporting bugs

If you think you found a bug in `resourcecode`, even if you are unsure, please let me know. The
easiest way is to send me an [email](mailto:nicolas.raillard@ifremer.fr).

Please try to create a reproducible example with the minimal amount of code required to reproduce the bug you encountered.

## Adding or requesting new functionalities

Whenever possible, we will try to add new functionalities to  `resourcecode` package depending on user's needs and feedbacks. Proposed functionalities are tracked with issues, so please have a look to see what are the plans.

If you plan to develop new functionalities, you can fork the repository on GitLab to work on the patch.
Get in touch with the maintainer to refine and prioritize your issue.

## Licensing

All contributed code will be licensed under a GPL-3 license with authorship attribution. If you did not write the code yourself, it is your responsibility to ensure that the existing license is compatible and included in the contributed files.

## Code of conduct

Please note that `resourcecode` is released with a [Contributor Code of
Conduct](https://ropensci.org/code-of-conduct/). By contributing to this project
you agree to abide by its terms.

# Acknowledgments

The **ResourceCODE** project, under which this package have been developed,
has received support under the framework of the OCEANERA-NET COFUND project,
with funding provided by national/ regional sources and co-funding by the
European Union's Horizon 2020 research and innovation program.

The partners of the projet (EMEC, IFREMER, CentraleNantes, Ocean Data Lab,
Smart Bay Ireland, University College Dublin, INNOSEA and University of Edinburgh)
contributed to this this toolbox and transfered the copyright to IFREMER. They all
agreed to the published License (GPL v3).

The `resourcecode` Python module was developed by [Logilab](https://logilab.fr/)
based on various scientific codes written by the partners of the **ResourceCODE**
projet. The copyright have been transfered to IFREMER. More information at https://resourcecode.ifremer.fr.
