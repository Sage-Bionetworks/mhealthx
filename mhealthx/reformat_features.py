#!/usr/bin/env python
"""
Functions for formatting feature extraction commands' output files.

The desired output is a list with two rows:
1. feature names
2. feature values

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def format_openSMILE_output(input_file):
    """
    Format the output from openSMILE's SMILExtract command.

    Parameters
    ----------
    input_file : string
        openSMILE's SMILExtract command output .csv file

    Returns
    -------
    feature_table : pandas DataFrame (N rows x 2 columns)
        feature names and values

    Examples
    --------
    >>> from mhealthx.reformat_features import format_openSMILE_output
    >>> input_file = '/Users/arno/csv/test1.csv'
    >>> feature_table = format_openSMILE_output(input_file)

    """
    import os
    import pandas as pd

    # Settings:
    name_line_from_top = 3
    data_line_from_left = 1
    data_line_from_right = 1
    left_strip = '@attribute'
    right_strip = 'numeric\n'

    # Check to make sure input_file exists:
    if not type(input_file) == str:
        raise IOError("'input_file' should be a file path string.")
    if not os.path.isfile(input_file):
        raise IOError("{0} does not exist.".format(input_file))

    # Open input_file:
    f = open(input_file, 'r')
    lines = f.readlines()

    # Extract feature values from input_file:
    feature_values = lines[len(lines) - 1]
    feature_values = feature_values.split(',')
    feature_values = feature_values[data_line_from_left:-data_line_from_right]

    # Extract (and format) feature names from input_file:
    feature_names = lines[name_line_from_top:name_line_from_top +
                                             len(feature_values)]
    for i, line in enumerate(feature_names):
        feature_names[i] = line.lstrip(left_strip).rstrip(right_strip).strip()

    feature_table = pd.DataFrame(feature_values).transpose()
    feature_table.columns = feature_names

    return feature_table
