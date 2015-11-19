#!/usr/bin/env python
"""
Functions that run feature extraction programs and save feature tables.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def make_row_table(file_path, table_stem, save_rows, row, row_data,
                   feature_row=None):
    """
    Function to store feature row to a table.

    Parameters
    ----------
    file_path : string
        path to accelerometer file (from row)
    table_stem : string
        prepend to output table file
    save_rows : Boolean
        save individual rows rather than write to a single feature table?
    row : pandas Series
        row to prepend, unaltered, to feature row (if feature_row is None)
    row_data : pandas Series (if feature_row is None)
        feature row
    feature_row : pandas Series
        feature row (skip feature row construction)

    Returns
    -------
    feature_row : pandas Series
        row combining the original row with a row of openSMILE feature values
    feature_table : string
        output table file (full path)
    """
    import os
    import pandas as pd

    from mhealthx.xio import row_to_table

    if not feature_row:
        if isinstance(row, pd.Series) and not row.empty:
            feature_row = pd.concat([row, row_data.transpose()], axis=0)
            feature_row = feature_row.transpose()
        else:
            feature_row = row_data

    # Write feature row to a table or append to a feature table:
    if save_rows:
        if file_path.endswith('.csv'):
            feature_table = '{0}_{1}'.format(table_stem,
                                             os.path.basename(file_path))
        else:
            feature_table = '{0}_{1}.csv'.format(table_stem,
                                                 os.path.basename(file_path))
        try:
            feature_row.to_csv(feature_table)
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            feature_table = None
    else:
        if table_stem.endswith('.csv'):
            feature_table = table_stem
        else:
            feature_table = table_stem + '.csv'
        try:
            row_to_table(feature_row, feature_table)
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            feature_table = None

    return feature_row, feature_table


def run_openSMILE(audio_file, command, flag1, flags, flagn, args, closing,
                  row, table_stem, save_rows):
    """
    Run openSMILE to process audio file and store feature row to a table.

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

    from mhealthx.utilities import run_command
    from mhealthx.extract import make_row_table

    # Run openSMILE's SMILExtract audio feature extraction command.
    feature_row = None
    feature_table = None
    if os.path.isfile(audio_file):
        argn = ''.join([audio_file.strip('.wav'),'.csv'])
        cline, args, arg1, argn = run_command(command=command,
                                              flag1=flag1,
                                              arg1=audio_file,
                                              flags=flags,
                                              args=args,
                                              flagn=flagn,
                                              argn=argn,
                                              closing=closing)

        # Extract row data from openSMILE:
        try:
            row_data = pd.read_csv(argn, sep=";")
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        # Write feature row to a table or append to a feature table:
        else:
            feature_row, feature_table = make_row_table(argn, table_stem,
                                                        save_rows, row,
                                                        row_data, feature_row)
    return feature_row, feature_table


def run_pyGait(data, t, sample_rate, duration, threshold, order, cutoff,
               distance, row, file_path, table_stem, save_rows=False):
    """
    Run pyGait (replication of iGAIT) accelerometer feature extraction code.

    Steps ::
        1. Run pyGait accelerometer feature extraction.
        2. Construct a feature row from the original and pyGait rows.
        3. Write the feature row to a table or append to a feature table.

    Parameters
    ----------
    data : numpy array
        accelerometer data along any (preferably forward walking) axis
    t : list or numpy array
        accelerometer time points
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
    distance : float
        estimate of distance traversed
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
    >>> from mhealthx.extractors.pyGait import project_on_walking_direction
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> start = 150
    >>> device_motion = False
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> stride_fraction = 1.0/8.0
    >>> threshold0 = 0.5
    >>> threshold = 0.2
    >>> order = 4
    >>> cutoff = max([1, sample_rate/10])
    >>> distance = None
    >>> row = pd.Series({'a':[1], 'b':[2], 'c':[3]})
    >>> file_path = '/fake/path'
    >>> table_stem = './walking'
    >>> save_rows = True
    >>> px, py, pz = project_on_walking_direction(ax, ay, az, t, sample_rate, stride_fraction, threshold0, order, cutoff)
    >>> feature_row, feature_table = run_pyGait(py, t, sample_rate, duration, threshold, order, cutoff, distance, row, file_path, table_stem, save_rows)

    """
    import pandas as pd

    from mhealthx.extractors.pyGait import heel_strikes, gait
    from mhealthx.extract import make_row_table

    # Extract features from data:
    strikes, strike_indices = heel_strikes(data, sample_rate, threshold,
                                           order, cutoff, False, t)

    number_of_steps, cadence, velocity, avg_step_length, avg_stride_length,\
    step_durations, avg_step_duration, sd_step_durations, strides, \
    stride_durations, avg_number_of_strides, avg_stride_duration, \
    sd_stride_durations, step_regularity, stride_regularity, \
    symmetry = gait(strikes, data, duration, distance)

    # Create row of data:
    row_data = pd.DataFrame({'number_of_steps': number_of_steps,
                             'cadence': cadence,
                             'velocity': velocity,
                             'avg_step_length': avg_step_length,
                             'avg_stride_length': avg_stride_length,
                             'avg_step_duration': avg_step_duration,
                             'sd_step_durations': sd_step_durations,
                             'avg_number_of_strides': avg_number_of_strides,
                             'avg_stride_duration': avg_stride_duration,
                             'sd_stride_durations': sd_stride_durations,
                             'step_regularity': step_regularity,
                             'stride_regularity': stride_regularity,
                             'symmetry': symmetry},
                            index=[0])

    # Write feature row to a table or append to a feature table:
    feature_row, feature_table = make_row_table(file_path, table_stem,
                                                save_rows, row, row_data,
                                                feature_row=None)
    return feature_row, feature_table


def run_signal_features(data, row, file_path, table_stem, save_rows=False):
    """
    Extract various features from time series data.

    Parameters
    ----------
    data : numpy array of floats
        time series data
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
    >>> from mhealthx.extract import run_signal_features
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> start = 150
    >>> device_motion = False
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, data, az = axyz
    >>> row = pd.Series({'a':[1], 'b':[2], 'c':[3]})
    >>> file_path = '.'
    >>> table_stem = './walking'
    >>> save_rows = True
    >>> feature_row, feature_table = run_signal_features(data, row, file_path, table_stem, save_rows)

    """
    import pandas as pd

    from mhealthx.signals import signal_features
    from mhealthx.extract import make_row_table

    # Extract different features from the data:
    rms, entropy = signal_features(data)

    # Create row of data:
    row_data = pd.DataFrame({'rms': rms,
                             'entropy': entropy},
                            index=[0])

    # Write feature row to a table or append to a feature table:
    feature_row, feature_table = make_row_table(file_path, table_stem,
                                                save_rows, row, row_data,
                                                feature_row=None)
    return feature_row, feature_table


def run_quality(gx, gy, gz, row, file_path, table_stem, save_rows=False):
    """
    Extract various features from time series data.

    Parameters
    ----------
    gx : list
        x-axis gravity acceleration
    gy : list
        y-axis gravity acceleration
    gz : list
        z-axis gravity acceleration
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
    >>> from mhealthx.extract import run_quality
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> #ax, ay, az = axyz
    >>> gx, gy, gz = gxyz
    >>> #rx, ry, rz = rxyz
    >>> #uw, ux, uy, uz = wxyz
    >>> row = pd.Series({'a':[1], 'b':[2], 'c':[3]})
    >>> file_path = '.'
    >>> table_stem = './walking'
    >>> save_rows = True
    >>> feature_row, feature_table = run_quality(gx, gy, gz, row, file_path, table_stem, save_rows)

    """
    import pandas as pd

    from mhealthx.signals import accelerometer_signal_quality
    from mhealthx.extract import make_row_table

    # Compute different quality measures from the data:
    min_mse, vertical = accelerometer_signal_quality(gx, gy, gz)

    # Create row of data:
    row_data = pd.DataFrame({'min_mse': min_mse,
                             'vertical': vertical},
                             index=[0])

    # Write feature row to a table or append to a feature table:
    feature_row, feature_table = make_row_table(file_path, table_stem,
                                                save_rows, row, row_data,
                                                feature_row=None)
    return feature_row, feature_table


# ============================================================================
if __name__ == '__main__':

    pass