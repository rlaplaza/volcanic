volcanic: Automated Generator of Volcano Plots
==============================================
[![DOI](https://zenodo.org/badge/381737392.svg)](https://zenodo.org/badge/latestdoi/381737392)

![volcanic logo](./images/volcanic_logo.png)

## Contents
* [About](#about-)
* [Install](#install-)
* [Examples](#examples-)
* [Citation](#citation-)

## About [↑](#about)

The code runs on pure python with minimal dependencies: 
- `numpy`
- `scipy`
- `matplotlib`
- `pandas`


## Install [↑](#install)

Download and add volcanic.py to your path. No strings attached. Run as:

```python
python volcanic.py [-h] [-version] -i [FILENAMES] [-df DFILENAMES] [-nd ND] [-v VERB] [-r RUNMODE] [-lsfer | -thermo | -kinetic | -es | -tof | -all] [-T TEMP] [-pm PLOTMODE] [-ic IC] [-fc FC]
                [-rm RMARGIN] [-lm LMARGIN] [-np NPOINTS] [-d] [-is IMPUTER_STRAT] [-refill]
```

You can also execute:

```python 
python setup.py install
```

to install volcanic as a python module. Afterwards, you can call volcanic as:

```python 
python -m volcanic [-h] [-version] -i [FILENAMES] [-df DFILENAMES] [-nd ND] [-v VERB] [-r RUNMODE] [-lsfer | -thermo | -kinetic | -es | -tof | -all] [-T TEMP] [-pm PLOTMODE] [-ic IC] [-fc FC]
                [-rm RMARGIN] [-lm LMARGIN] [-np NPOINTS] [-d] [-is IMPUTER_STRAT] [-refill]
```

Options can be consulted using the `-h` flag in either case. The help menu is quite detailed.

## Examples [↑](#examples)

The examples subdirectory contains a copious amount of tests which double as examples. Any of the data files can be run as:

```python
python volcanic.py -i [FILENAME]
```

This will query the user for options and generate the volcano plots as png images. Options can be consulted with the `-h` flag.

The input of volcanic.py is a `pandas` compatible dataframe, which includes plain .csv and .xls files. 

Regarding format, volcanic.py expects headers for all columns. The first column must contain names/identifiers. Then, volcanic.py expects a number of columns with relative free energies for the species in the catalytic cycle (in order of appearance), whose headers must contain "TS" if the species is a transition state, and a final column whose header is "Product" containing the reaction energy. Non-energy descriptors can be input as a separate file using the `-df` flag or as extra columns whose headers contain the word "Descriptor".

High verbosity levels (`-h`) will print the output as csv files as well, which can be used to plot your volcano plot or activity map as you wish. An example is found in the `pretty_plotting_example` directory in this repository.


## Citation [↑](#citation)

Please cite the accompanying manuscript, which clarifies the details of volcano plot construction. You can find it [here](https://rdcu.be/cT7uu).

```
Laplaza, R., Das, S., Wodrich, M.D. et al. Constructing and interpreting volcano plots and activity maps to navigate homogeneous catalyst landscapes. <b>Nat Protoc (2022)</b>. https://doi.org/10.1038/s41596-022-00726-2
```

---


