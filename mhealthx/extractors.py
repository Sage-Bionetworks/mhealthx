#!/usr/bin/env python
"""
Functions that run feature extraction programs.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def openSMILE(synapse_table, row, column_name, convert_file_append,
              convert_command, convert_input_args, convert_output_args,
              username, password, command, flag1, flags, flagn,
              args, closing, temporary_path, feature_table_path, save_rows):
    """
    Retrieve, convert, process audio file, and store feature row to a table.

    Steps ::
        1. Retrieve each row + audio file from a Synapse table.
        2. Convert voice file to .wav format.
        3. Run openSMILE's SMILExtract audio feature extraction command.
        4. Construct a feature row from the original and openSMILE rows.
        5. Write the feature row to a table or append to a feature table.

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    row : pandas Series or string
        row of a Synapse table converted to a Series or csv file
    column_name : string
        name of file handle column
    convert_file_append : string
        append to file name to indicate converted file format (e.g., '.wav')
    convert_command : string
        executable command without arguments
    convert_input_args : string
        arguments preceding input file name for convert_command
    convert_output_args : string
        arguments preceding output file name for convert_command
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
    temporary_path : string
        path for temporary output of audio files (optional, else cache dir)
    feature_table_path : string
        path to the output table file (parent directory)
    save_rows : Boolean
        save individual rows rather than write to a single feature table?

    Returns
    -------
    feature_row : pandas Series
        row combining the original row with a row of openSMILE feature values
    feature_table : string
        output table file (full path)

    Examples
    --------
    >>> import os
    >>> from mhealthx.extractors import openSMILE
    >>> from mhealthx.synapse_io import extract_rows, read_files_from_row
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> #row_series, row_files = extract_rows(synapse_table, save_path='.', limit=3, username='', password='')
    >>> row_path = '/homedir/mhealthx_cache/mhealthxprep/row_files'
    >>> row_files = [os.path.join(row_path, f)
    >>>          for i,f in enumerate(sorted(os.listdir(row_path)))
    >>>          if i < 3
    >>>          and os.path.isfile(os.path.join(row_path,f))]
    >>> column_name = 'audio_audio.m4a' #, 'audio_countdown.m4a']
    >>> out_path = os.path.abspath('.')
    >>> convert_file_append = '.wav'
    >>> convert_command = 'ffmpeg'
    >>> convert_input_args = '-i'
    >>> convert_output_args = '-ac 2'
    >>> username = ''
    >>> password = ''
    >>> command = 'SMILExtract'
    >>> flag1 = '-I'
    >>> flags = '-C'
    >>> flagn = '-csvoutput' #'-O'
    >>> thirdparty = '/software'
    >>> args = os.path.join(thirdparty, 'openSMILE-2.1.0', 'config', 'IS13_ComParE.conf')
    >>> closing = '-nologfile 1'
    >>> temporary_path = '/Users/arno/Desktop' #'/home/ubuntu'
    >>> feature_table_path = '.'
    >>> save_rows = True
    >>> for i in range(1):
    >>>     #row = row_series[i]
    >>>     row = row_files[i]
    >>>     row, filepath = read_files_from_row(synapse_table, row,
    >>>         column_name, out_path, username, password)
    >>>     print(row)
    >>>     feature_row, feature_table = openSMILE(synapse_table,
    >>>                      row, column_name, convert_file_append,
    >>>                      convert_command, convert_input_args,
    >>>                      convert_output_args, username, password, command,
    >>>                      flag1, flags, flagn, args, closing,
    >>>                      temporary_path, feature_table_path, save_rows)

    """
    import os
    import pandas as pd

    from mhealthx.data_io import get_convert_audio, row_to_table
    from mhealthx.utils import run_command

    #try:
    # 1. Retrieve each row + audio file from a Synapse table.
    # 2. Convert voice file to .wav format.
    out_path = temporary_path #os.path.abspath('.')
    row, new_file = get_convert_audio(synapse_table,
                                      row,
                                      column_name,
                                      convert_file_append,
                                      convert_command,
                                      convert_input_args,
                                      convert_output_args,
                                      out_path,
                                      username,
                                      password)

    # 3. Run openSMILE's SMILExtract audio feature extraction command.
    cline, args, arg1, argn = run_command(command=command,
                                          flag1=flag1,
                                          arg1=new_file,
                                          flags=flags,
                                          args=args,
                                          flagn=flagn,
                                          argn=''.join([new_file,'.csv']),
                                          closing=closing)

    # 4. Construct a feature row from the original and openSMILE rows.
    row_data = pd.read_csv(argn, sep=";")
    row_data = row_data.ix[0, :]
    feature_row = pd.concat([row, row_data], axis=0)

    # 5. Write the feature row to a table or append to a feature table.
    if save_rows:
        feature_table = os.path.join(feature_table_path,
                                     os.path.basename(argn))
        feature_row.to_csv(feature_table)
    else:
        feature_table = os.path.join(feature_table_path,
                        'phonation_features_openSMILE-2.1.0_IS13_ComParE.csv')
        row_to_table(feature_row, feature_table)

    # except:
    #     feature_row = None
    #     feature_table = None

    return feature_row, feature_table



# ============================================================================
if __name__ == '__main__':

    pass