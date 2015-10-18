#!/usr/bin/env python
"""
Functions that run feature extraction programs.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def openSMILE(audio_file, row, command, flag1, flags, flagn, args,
              closing, feature_table_path, feature_table_prepend, save_rows):
    """
    Process audio file and store feature row to a table.

    Steps ::
        1. Run openSMILE's SMILExtract audio feature extraction command.
        2. Construct a feature row from the original and openSMILE rows.
        3. Write the feature row to a table or append to a feature table.

    Parameters
    ----------
    audio_file : string
        full path to the input audio file
    row : pandas Series or string
        row to prepend, unaltered, to feature row
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
    feature_table_path : string
        path to the output table file (parent directory)
    feature_table_prepend : string
        prepend to output table file
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
    >>> from mhealthx.xio import get_convert_audio
    >>> from mhealthx.xio import extract_synapse_rows, read_file_from_synapse_table
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> row_series, row_files = extract_synapse_rows(synapse_table, save_path='.', limit=3, username='', password='')
    >>> column_name = 'audio_audio.m4a' #, 'audio_countdown.m4a']
    >>> convert_file_append = '.wav'
    >>> convert_command = 'ffmpeg'
    >>> convert_input_args = '-y -i'
    >>> convert_output_args = '-ac 2'
    >>> out_path = '.'
    >>> username = ''
    >>> password = ''
    >>> for i in range(1):
    >>>     row = row_series[i]
    >>>     row, filepath = read_file_from_synapse_table(synapse_table, row,
    >>>         column_name, out_path, username, password)
    >>>     print(row)
    >>>     row, audio_file = get_convert_audio(synapse_table,
    >>>                                       row, column_name,
    >>>                                       convert_file_append,
    >>>                                       convert_command,
    >>>                                       convert_input_args,
    >>>                                       convert_output_args,
    >>>                                       out_path, username, password)
    >>> import os
    >>> from mhealthx.extractors import openSMILE
    >>> command = 'SMILExtract'
    >>> flag1 = '-I'
    >>> flags = '-C'
    >>> flagn = '-csvoutput' #'-O'
    >>> thirdparty = '/software'
    >>> args = os.path.join(thirdparty, 'openSMILE-2.1.0', 'config',
    >>>                     'IS13_ComParE.conf')
    >>> closing = '-nologfile 1'
    >>> feature_table_path = '.'
    >>> feature_table_prepend = 'phonation_'
    >>> save_rows = True
    >>> feature_row, feature_table = openSMILE(audio_file, row, command,
    >>>                      flag1, flags, flagn, args, closing,
    >>>                      feature_table_path, feature_table_prepend, save_rows)

    """
    import os
    import pandas as pd

    from mhealthx.xio import row_to_table, run_command

    # Run openSMILE's SMILExtract audio feature extraction command.
    feature_row = None
    feature_table = None
    if os.path.isfile(audio_file):
        argn = ''.join([audio_file,'.csv'])
        cline, args, arg1, argn = run_command(command=command,
                                              flag1=flag1,
                                              arg1=audio_file,
                                              flags=flags,
                                              args=args,
                                              flagn=flagn,
                                              argn=argn,
                                              closing=closing)

        # 4. Construct a feature row from the original and openSMILE rows.
        try:
            row_data = pd.read_csv(argn, sep=";")
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        else:
            row_data = row_data.ix[0, :]
            feature_row = pd.concat([row, row_data], axis=0)

            # 5. Write feature row to a table or append to a feature table.
            if save_rows:
                feature_table = os.path.join(feature_table_path,
                                             os.path.basename(argn))
                try:
                    feature_row.to_csv(feature_table)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
                    feature_table = None
            else:
                conf = feature_table_prepend + \
                       'openSMILE-2.1.0_IS13_ComParE.csv'
                feature_table = os.path.join(feature_table_path, conf)
                try:
                    row_to_table(feature_row, feature_table)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
                    feature_table = None

    return feature_row, feature_table



# ============================================================================
if __name__ == '__main__':

    pass