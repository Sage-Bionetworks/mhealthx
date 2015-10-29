#!/usr/bin/env python
"""
Functions that run feature extraction programs.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def run_openSMILE(audio_file, command, flag1, flags, flagn, args, closing,
                  row, table_stem, save_rows):
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
    row : pandas Series
        row to prepend, unaltered, to feature row
    table_stem : string
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
    >>> # openSMILE setup, with examples below:
    >>>
    >>> import os
    >>> from mhealthx.extract import run_openSMILE
    >>> command = 'SMILExtract'
    >>> flag1 = '-I'
    >>> flags = '-C'
    >>> flagn = '-csvoutput'
    >>> args = os.path.join('/software', 'openSMILE-2.1.0', 'config',
    >>>                     'IS13_ComParE.conf')
    >>> closing = '-nologfile 1'
    >>> save_rows = True
    >>>
    >>> # Example: phonation data
    >>>
    >>> from mhealthx.xio import get_convert_audio
    >>> from mhealthx.xio import extract_synapse_rows, read_file_from_synapse_table
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> row_series, row_files = extract_synapse_rows(synapse_table, save_path='.', limit=1, username='', password='')
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
    >>>                                         row, column_name,
    >>>                                         convert_file_append,
    >>>                                         convert_command,
    >>>                                         convert_input_args,
    >>>                                         convert_output_args,
    >>>                                         out_path, username, password)
    >>> table_stem = './phonation'
    >>> feature_row, feature_table = run_openSMILE(audio_file, command,
    >>>                      flag1, flags, flagn, args, closing,
    >>>                      row, table_stem, save_rows)

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
            if isinstance(row, pd.Series) and not row.empty:
                #row_data = row_data.ix[0, :]
                #feature_row = row.append(row_data.transpose())
                feature_row = pd.concat([row, row_data.transpose()], axis=0)
                feature_row = feature_row.transpose()
            else:
                feature_row = row_data

            # 5. Write feature row to a table or append to a feature table.
            if save_rows:
                feature_table = '{0}_{1}'.format(table_stem,
                                                 os.path.basename(argn))
                try:
                    feature_row.to_csv(feature_table)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
                    feature_table = None
            else:
                feature_table = table_stem + '.csv'
                try:
                    row_to_table(feature_row, feature_table)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
                    feature_table = None

    return feature_row, feature_table


def run_pyGait(x, y, z, t, sample_rate, duration, threshold, order, cutoff, \
              row, file_path, table_stem, save_rows=False):
    """
    Process audio file and store feature row to a table.

    Steps ::
        1. Run pyGait accelerometer feature extraction.
        2. Construct a feature row from the original and pyGait rows.
        3. Write the feature row to a table or append to a feature table.

    Parameters
    ----------
    x : list
        x-axis accelerometer data
    y : list
        y-axis accelerometer data
    z : list
        z-axis accelerometer data
    t : list
        time points for accelerometer data
    sample_rate : float
        sample rate of accelerometer reading (Hz)
    duration : float
        duration of accelerometer reading (s)
    threshold : float
        ratio to the maximum value of the anterior-posterior acceleration
    order : integer
        order of the Butterworth filter
    cutoff : integer
        cutoff frequency of the Butterworth filter (Hz)
    row : pandas Series
        row to prepend, unaltered, to feature row
    file_path : string
        path to accelerometer file (from row)
    table_stem : string
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
    >>> import pandas as pd
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.extract import run_pyGait
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> x, y, z, t, sample_rate, duration = read_accel_json(input_file)
    >>> threshold = 0.2
    >>> order = 4
    >>> cutoff = 5
    >>> data = y
    >>> row = pd.Series({'a':[1], 'b':[2], 'c':[3]})
    >>> file_path = '/fake/path'
    >>> table_stem = './walking'
    >>> save_rows = True
    >>> feature_row, feature_table = run_pyGait(x, y, z, t, sample_rate, duration, threshold, order, cutoff, row, file_path, table_stem, save_rows)

    """
    import os
    import pandas as pd

    from mhealthx.xio import row_to_table, read_file_from_synapse_table
    from mhealthx.extractors.pyGait import gait

    # Run (replication of) iGAIT's accelerometer feature extraction code:
    heel_strikes, number_of_steps, cadence, step_durations, \
    avg_step_duration, sd_step_durations, strides, stride_durations, \
    avg_number_of_strides, avg_stride_duration, sd_stride_durations, \
    step_regularity_x, step_regularity_y, step_regularity_z, \
    stride_regularity_x, stride_regularity_y, stride_regularity_z, \
    symmetry_x, symmetry_y, symmetry_z = gait(x, y, z, t, sample_rate, \
                                              duration, threshold, order, \
                                              cutoff)
    row_data = pd.DataFrame({'number_of_steps' : number_of_steps,
                             'cadence' : cadence,
                             'avg_step_duration' : avg_step_duration,
                             'sd_step_durations' : sd_step_durations,
                             'avg_number_of_strides' : avg_number_of_strides,
                             'avg_stride_duration' : avg_stride_duration,
                             'sd_stride_durations' : sd_stride_durations,
                             'step_regularity_x' : step_regularity_x,
                             'step_regularity_y' : step_regularity_y,
                             'step_regularity_z' : step_regularity_z,
                             'stride_regularity_x' : stride_regularity_x,
                             'stride_regularity_y' : stride_regularity_y,
                             'stride_regularity_z' : stride_regularity_z,
                             'symmetry_x' : symmetry_x,
                             'symmetry_y' : symmetry_y,
                             'symmetry_z' : symmetry_z}, index=[0])

    if isinstance(row, pd.Series) and not row.empty:
        feature_row = pd.concat([row, row_data.transpose()], axis=0)
        feature_row = feature_row.transpose()
    else:
        feature_row = row_data

    # 5. Write feature row to a table or append to a feature table.
    if save_rows:
        feature_table = '{0}_{1}.csv'.format(table_stem,
                                             os.path.basename(file_path))
        try:
            feature_row.to_csv(feature_table)
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            feature_table = None
    else:
        feature_table = table_stem + '.csv'
        try:
            row_to_table(feature_row, feature_table)
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            feature_table = None

    return feature_row, feature_table


# ============================================================================
if __name__ == '__main__':

    pass