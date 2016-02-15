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
        row combining the original row with a row of feature values
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
        if not file_path.endswith('.csv'):
            file_path = file_path + '.csv'
        feature_table = os.path.join(table_stem, os.path.basename(file_path))
        try:
            feature_row.to_csv(feature_table)
        except IOError as e:
            import traceback; traceback.print_exc()
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
            import traceback; traceback.print_exc()
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
            import traceback; traceback.print_exc()
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            print("filename = ", argn)
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
        row combining the original row with a row of pyGait feature values
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
        row combining the original row with a row of signal feature values
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
    num, min, max, rng, avg, std, med, mad, kurt, skew, cvar, lower25, \
    upper25, inter50, rms, entropy, tk_energy = signal_features(data)

    # Create row of data:
    row_data = pd.DataFrame({'num': num,
                             'min': min,
                             'max': max,
                             'rng': rng,
                             'avg': avg,
                             'std': std,
                             'med': med,
                             'mad': mad,
                             'kurt': kurt,
                             'skew': skew,
                             'cvar': cvar,
                             'lower25': lower25,
                             'upper25': upper25,
                             'inter50': inter50,
                             'rms': rms,
                             'entropy': entropy,
                             'tk_energy': tk_energy},
                            index=[0])

    # Write feature row to a table or append to a feature table:
    feature_row, feature_table = make_row_table(file_path, table_stem,
                                                save_rows, row, row_data,
                                                feature_row=None)
    return feature_row, feature_table


def run_sdf_features(data, number_of_symbols, row, file_path, table_stem, save_rows):
    """
    Extract symbolic dynamic filtering features.

    Parameters
    ----------
    data : numpy array
    number_of_symbols : integer
        number of symbols for symbolic dynamic filtering method

    Returns
    -------
    feature_row : pandas Series
        row combining the original row with a row of SDF feature values
    feature_table : string
        output table file (full path)

    Examples
    --------
    >>> import pandas as pd
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.extract import run_sdf_features
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> start = 150
    >>> device_motion = False
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, data, az = axyz
    >>> number_of_symbols = 4
    >>> row = pd.Series({'a':[1], 'b':[2], 'c':[3]})
    >>> file_path = '.'
    >>> table_stem = './walking'
    >>> save_rows = True
    >>> feature_row, feature_table = run_sdf_features(data, number_of_symbols, row, file_path, table_stem, save_rows)

    """
    import pandas as pd

    from mhealthx.extract import make_row_table
    from mhealthx.extractors.symbolic_dynamic_filtering import sdf_features

    sdf = sdf_features(data, number_of_symbols, pi_matrix_flag=False)

    # Create row of data:
    row_data = pd.DataFrame({'SDF eigenvector 1': sdf[0]}, index=[0])
    for isdf in range(1, len(sdf)):
        hdr = 'SDF eigenvalue ' + str(isdf + 1)
        df = pd.DataFrame({hdr: sdf[isdf]}, index=[0])
        row_data = pd.concat([row_data, df], axis=1,
                             join_axes=[row_data.index])

    # Write feature row to a table or append to a feature table:
    feature_row, feature_table = make_row_table(file_path, table_stem,
                                                save_rows, row, row_data,
                                                feature_row=None)
    return feature_row, feature_table


def run_tap_features(xtaps, ytaps, t, threshold,
                     row, file_path, table_stem, save_rows=False):
    """
    Run touch screen tap feature extraction methods.

    Parameters
    ----------
    xtaps : numpy array of integers
        x coordinates of touch screen where tapped
    ytaps : numpy array of integers
        y coordinates of touch screen where tapped
    t : numpy array of floats
        time points of taps
    threshold : integer
        x offset threshold for left/right press event (pixels)
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
        row combining the original row with a row of tap feature values
    feature_table : string
        output table file (full path)

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from mhealthx.extract import run_tap_features
    >>> xtaps = np.round(200 * np.random.random(100))
    >>> ytaps = np.round(300 * np.random.random(100))
    >>> t = np.linspace(1, 100, 100) / 30.0
    >>> threshold = 20
    >>> row = pd.Series({'a':[1], 'b':[2], 'c':[3]})
    >>> file_path = '.'
    >>> table_stem = './tapping'
    >>> save_rows = True
    >>> feature_row, feature_table = run_tap_features(xtaps, ytaps, t, threshold, row, file_path, table_stem, save_rows)

    """
    import pandas as pd

    from mhealthx.extractors.tapping import compute_tap_features
    from mhealthx.extract import make_row_table

    # Extract different features from the data:
    T = compute_tap_features(xtaps, ytaps, t, threshold)

    # Create row of data:
    row_data = pd.DataFrame({'num_taps': T.num_taps,
                             'num_taps_left': T.num_taps_left,
                             'num_taps_right': T.num_taps_right,
                             'time_rng': T.time_rng,
                             'intertap_gap10': T.intertap_gap10,
                             'intertap_gap25': T.intertap_gap25,
                             'intertap_gap50': T.intertap_gap50,
                             'intertap_num': T.intertap_num,
                             'intertap_min': T.intertap_min,
                             'intertap_max': T.intertap_max,
                             'intertap_rng': T.intertap_rng,
                             'intertap_avg': T.intertap_avg,
                             'intertap_std': T.intertap_std,
                             'intertap_med': T.intertap_med,
                             'intertap_mad': T.intertap_mad,
                             'intertap_kurt': T.intertap_kurt,
                             'intertap_skew': T.intertap_skew,
                             'intertap_cvar': T.intertap_cvar,
                             'intertap_lower25': T.intertap_lower25,
                             'intertap_upper25': T.intertap_upper25,
                             'intertap_inter50': T.intertap_inter50,
                             'intertap_rms': T.intertap_rms,
                             'intertap_entropy': T.intertap_entropy,
                             'intertap_tk_energy': T.intertap_tk_energy,
                             'xL_num': T.xL_num,
                             'xL_min': T.xL_min,
                             'xL_max': T.xL_max,
                             'xL_rng': T.xL_rng,
                             'xL_avg': T.xL_avg,
                             'xL_std': T.xL_std,
                             'xL_med': T.xL_med,
                             'xL_mad': T.xL_mad,
                             'xL_kurt': T.xL_kurt,
                             'xL_skew': T.xL_skew,
                             'xL_cvar': T.xL_cvar,
                             'xL_lower25': T.xL_lower25,
                             'xL_upper25': T.xL_upper25,
                             'xL_inter50': T.xL_inter50,
                             'xL_rms': T.xL_rms,
                             'xL_entropy': T.xL_entropy,
                             'xL_tk_energy': T.xL_tk_energy,
                             'xR_num': T.xR_num,
                             'xR_min': T.xR_min,
                             'xR_max': T.xR_max,
                             'xR_rng': T.xR_rng,
                             'xR_avg': T.xR_avg,
                             'xR_std': T.xR_std,
                             'xR_med': T.xR_med,
                             'xR_mad': T.xR_mad,
                             'xR_kurt': T.xR_kurt,
                             'xR_skew': T.xR_skew,
                             'xR_cvar': T.xR_cvar,
                             'xR_lower25': T.xR_lower25,
                             'xR_upper25': T.xR_upper25,
                             'xR_inter50': T.xR_inter50,
                             'xR_rms': T.xR_rms,
                             'xR_entropy': T.xR_entropy,
                             'xR_tk_energy': T.xR_tk_energy,
                             'driftL_min': T.driftL_min,
                             'driftL_max': T.driftL_max,
                             'driftL_rng': T.driftL_rng,
                             'driftL_avg': T.driftL_avg,
                             'driftL_std': T.driftL_std,
                             'driftL_med': T.driftL_med,
                             'driftL_mad': T.driftL_mad,
                             'driftL_kurt': T.driftL_kurt,
                             'driftL_skew': T.driftL_skew,
                             'driftL_cvar': T.driftL_cvar,
                             'driftL_lower25': T.driftL_lower25,
                             'driftL_upper25': T.driftL_upper25,
                             'driftL_inter50': T.driftL_inter50,
                             'driftL_rms': T.driftL_rms,
                             'driftL_entropy': T.driftL_entropy,
                             'driftL_tk_energy': T.driftL_tk_energy,
                             'driftR_min': T.driftR_min,
                             'driftR_max': T.driftR_max,
                             'driftR_rng': T.driftR_rng,
                             'driftR_avg': T.driftR_avg,
                             'driftR_std': T.driftR_std,
                             'driftR_med': T.driftR_med,
                             'driftR_mad': T.driftR_mad,
                             'driftR_kurt': T.driftR_kurt,
                             'driftR_skew': T.driftR_skew,
                             'driftR_cvar': T.driftR_cvar,
                             'driftR_lower25': T.driftR_lower25,
                             'driftR_upper25': T.driftR_upper25,
                             'driftR_inter50': T.driftR_inter50,
                             'driftR_rms': T.driftR_rms,
                             'driftR_entropy': T.driftR_entropy,
                             'driftR_tk_energy': T.driftR_tk_energy},
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
        row combining the original row with a row of quality measures
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