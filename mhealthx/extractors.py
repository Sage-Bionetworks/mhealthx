#!/usr/bin/env python
"""
Functions that run feature extraction programs.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def openSMILE(synapse_table, row, column_name, rename_file_append,
              convert_file_append, convert_command, convert_input_args,
              convert_output_args, out_path, username, password, command,
              flag1, flags, flagn, args, closing, feature_table):
    """
    Retrieve, convert, process audio file, and store feature row to a table.

    Steps ::
        1. Retrieve each row + audio file from a Synapse table.
        2. Append file name with ".m4a".
        3. Convert voice file to .wav format.
        4. Run openSMILE's SMILExtract audio feature extraction command.
        5. Format openSMILE arff output as a (DataFrame) row.
        6. Construct a feature row from the original and openSMILE rows.
        7. Write the feature row to a feature table.

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    row : pandas DataFrame or string
        row of a Synapse table converted to a dataframe or csv file
    column_name : string
        name of file handle column
    rename_file_append : string
        append to file name prior to conversion (e.g., '.m4a')
    convert_file_append : string
        append to file name to indicate converted file format (e.g., '.wav')
    convert_command : string
        executable command without arguments
    convert_input_args : string
        arguments preceding input file name for convert_command
    convert_output_args : string
        arguments preceding output file name for convert_command
    out_path : string
        a local path in which to store downloaded files. If None, stores them in (~/.synapseCache)
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)
    command : string
        name of command: "SMILExtract"
    flag1 : string
        optional first command line flag
    flags : string or list of strings
        command line flags precede their respective args: ["-C", "-I", "-O"]
    flagn : string
        optional last command line flag
    args : string or list of strings
        command line arguments: ["config.conf", "input.wav", "output.csv"]
    closing : string
        closing string in command
    feature_table : string
        write row to this output table file (full path)

    Returns
    -------
    feature_row : pandas DataFrame
        row combining the original row with a row of openSMILE feature values

    Examples
    --------
    >>> import os
    >>> from mhealthx.extractors import openSMILE
    >>> from mhealthx.synapse_io import extract_rows, read_files_from_row
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> row_dataframes, row_files = extract_rows(synapse_table, save_path='.', limit=3, username='', password='')
    >>> column_name = 'audio_audio.m4a' #, 'audio_countdown.m4a']
    >>> rename_file_append = '.m4a'
    >>> convert_file_append = '.wav'
    >>> convert_command = 'ffmpeg'
    >>> convert_input_args = '-i'
    >>> convert_output_args = '-ac 2'
    >>> out_path = os.path.abspath('.')
    >>> username = ''
    >>> password = ''
    >>> command = 'SMILExtract'
    >>> flag1 = '-I'
    >>> flags = '-C'
    >>> flagn = '-O'
    >>> thirdparty = '/software'
    >>> args = os.path.join(thirdparty, 'openSMILE-2.1.0', 'config', 'IS13_ComParE.conf')
    >>> closing = '-nologfile 1'
    >>> feature_table = feature_table = '/homedir/mhealthx_cache/mhealthx/feature_tables/phonation_features_openSMILE-2.1.0_IS13_ComParE.csv'
    >>> for i in range(1):
    >>>     row = row_dataframes[i]
    >>>     row, filepath = read_files_from_row(synapse_table, row,
    >>>         column_name, out_path, username, password)
    >>>     print(row)
    >>> row_data = openSMILE(synapse_table, row, column_name, rename_file_append,
    >>>                      convert_file_append, convert_command, convert_input_args,
    >>>                      convert_output_args, out_path, username, password, command,
    >>>                      flag1, flags, flagn, args, closing, feature_table)

    """
    import os
    import pandas as pd

    from mhealthx.data_io import get_convert_audio, arff_to_csv, row_to_table
    from mhealthx.utils import run_command


    # 1. Retrieve each row + audio file from a Synapse table.
    # 2. Append file name with ".m4a".
    # 3. Convert voice file to .wav format.
    out_path = os.path.abspath('.')
    row, converted = get_convert_audio(synapse_table,
                                       row,
                                       column_name,
                                       rename_file_append,
                                       convert_file_append,
                                       convert_command,
                                       convert_input_args,
                                       convert_output_args,
                                       out_path,
                                       username,
                                       password)

    # 4. Run openSMILE's SMILExtract audio feature extraction command.
    cline, args, arg1, argn = run_command(command=command,
                                          flag1=flag1,
                                          arg1=converted,
                                          flags=flags,
                                          args=args,
                                          flagn=flagn,
                                          argn=''.join([converted, '.csv']),
                                          closing=closing)

    # 5. Format openSMILE arff output as a (DataFrame) row.
    row_data, output_csv_file = arff_to_csv(arff_file=argn,
                                            output_csv_file=None)

    # 6. Construct a feature row from the original and openSMILE rows.
    feature_row = pd.concat([row, row_data], axis=1)

    # 7. Write the feature row to a feature table.
    # if feature_table:
    #     row_to_table(feature_row, feature_table)

    return feature_row



# ============================================================================
if __name__ == '__main__':

    pass