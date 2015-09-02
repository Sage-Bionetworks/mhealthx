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


def format_SMILExtract_output(in_file):
    """
    Format openSMILE's SMILExtract command output .csv file.

    Parameters
    ----------
    in_file : string
        openSMILE's SMILExtract command output .csv file

    Returns
    -------
    feature_names : list of strings
        feature names
    feature_values : list of floats
        feature values

    Examples
    --------
    >>> from mhealthx.files_to_features import format_SMILExtract_output
    >>> in_file = '/Users/arno/csv/test1.csv'
    >>> feature_names, feature_values = format_SMILExtract_output(in_file)

    """
    import os

    # Settings:
    line_from_top = 3
    line_from_bottom = 6
    data_line_from_bottom = 0
    data_line_from_left = 1
    data_line_from_right = 1
    left_strip = '@attribute'
    right_strip = 'numeric\n'

    # Check to make sure in_file exists:
    if not type(in_file) == str:
        raise IOError("'in_file' should be a file path string.")
    if not os.path.isfile(in_file):
        raise IOError("{0} does not exist.".format(in_file))

    # Open in_file:
    f = open(in_file, 'r')
    lines = f.readlines()

    # Extract feature values from in_file:
    feature_values = lines[len(lines) - data_line_from_bottom - 1]
    feature_values = feature_values.split(',')
    feature_values = feature_values[data_line_from_left:-data_line_from_right]

    # Extract (and format) feature names from in_file:
    feature_names = lines[line_from_top:len(lines) - line_from_bottom - 1]
    for i, line in enumerate(feature_names):
        feature_names[i] = line.lstrip(left_strip).rstrip(right_strip).strip()

    return feature_names, feature_values
