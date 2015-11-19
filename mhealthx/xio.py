#!/usr/bin/env python
"""
Utility and I/O functions to read and write data files or Synapse tables.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def extract_synapse_rows(synapse_table, save_path=None, limit=None,
                         username='', password=''):
    """
    Extract rows from a Synapse table.

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    save_path : string
        save rows as separate files in this path, unless empty or None
    limit : integer or None
        limit to number of rows returned by the query
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    rows : list of pandas Series
        each row of a Synapse table
    row_files: list of strings
        file names corresponding to each of the rows

    Examples
    --------
    >>> from mhealthx.xio import extract_synapse_rows
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> save_path = '.'
    >>> limit = 3
    >>> username = ''
    >>> password = ''
    >>> rows, row_files = extract_synapse_rows(synapse_table, save_path, limit, username='', password='')

    """
    import os
    import pandas as pd
    import synapseclient

    # Log in to Synapse:
    syn = synapseclient.Synapse()
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Synapse table query:
    if limit:
        limit_string = 'limit {0}'.format(limit)
    else:
        limit_string = ''
    try:
        results = syn.tableQuery('select * from {0} {1}'.
                                 format(synapse_table, limit_string))
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        rows = None
        row_files = None
    else:
        # Column headers:
        headers = {header['name']: i for i, header
                   in enumerate(results.headers)}
        # Rows:
        rows = []
        row_files = []
        for irow, row in enumerate(results):
            row_map = {col:row[i] for col,i in headers.iteritems()}
            columns = row_map.keys()
            values = [unicode(x) for x in row_map.values()]
            row_series = pd.Series(values, columns)
            if save_path:
                csv_file = 'row{0}_v{1}_{2}'.format(row_map['ROW_ID'],
                                                    row_map['ROW_VERSION'],
                                                    row_map['recordId'])
                csv_file = os.path.join(save_path, csv_file)
                try:
                    row_series.to_csv(csv_file)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
                else:
                    rows.append(row_series)
                    row_files.append(csv_file)

    return rows, row_files


def read_file_from_synapse_table(synapse_table, row, column_name,
                                 out_path=None, username='', password=''):
    """
    Read data from a row of a Synapse table.

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    row : pandas Series or string
        row of a Synapse table converted to a Series or csv file
    column_name : string
        name of file handle column
    out_path : string
        a local path in which to store downloaded files
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    row : pandas Series
        same as passed in: row of a Synapse table as a file or Series
    filepath : string
        downloaded file (full path)

    Examples
    --------
    >>> from mhealthx.xio import extract_synapse_rows, read_file_from_synapse_table
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> save_path = '.'
    >>> limit = 3
    >>> username = ''
    >>> password = ''
    >>> rows, row_files = extract_synapse_rows(synapse_table, save_path, limit, username='', password='')
    >>> column_name = 'audio_audio.m4a' #, 'audio_countdown.m4a']
    >>> out_path = None
    >>> for i in range(3):
    >>>     row = rows[i]
    >>>     row, filepath = read_file_from_synapse_table(synapse_table, row, column_name, out_path, username, password)
    >>>     print(row)

    """
    import pandas as pd
    import synapseclient

    if type(row) == pd.Series:
        pass
    elif type(row) == str:
        # Read row from csv file to pandas Series:
        row = pd.Series.from_csv(row)
    else:
        raise IOError("row should be a pandas Series or a file string")

    # Log in to Synapse:
    syn = synapseclient.Synapse()
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Try to download file with column_name in row:
    try:
        if not out_path:
            out_path='./row{0}_v{1}_{2}'.format(row['ROW_ID'],
                                                row['ROW_VERSION'],
                                                row['recordId'])
        fileinfo = syn.downloadTableFile(synapse_table,
                            rowId=row['ROW_ID'][0],
                            versionNumber=row['ROW_VERSION'][0],
                            column=column_name,
                            downloadLocation=out_path)
        filepath = fileinfo['path']
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        filepath = None

    return row, filepath


def row_to_table(row_data, output_table):
    """
    Add row to table using nipype (thread-safe in multi-processor execution).

    (Requires Python module lockfile)

    Parameters
    ----------
    row_data : pandas Series
        row of data
    output_table : string
        add row to this table file

    Examples
    --------
    >>> import pandas as pd
    >>> from mhealthx.xio import row_to_table
    >>> row_data = pd.Series({'A': ['A0'], 'B': ['B0'], 'C': ['C0']})
    >>> output_table = 'test.csv'
    >>> row_to_table(row_data, output_table)
    """
    from nipype.algorithms import misc

    addrow = misc.AddCSVRow()
    addrow.inputs.in_file = output_table
    addrow.inputs.set(**row_data.to_dict())
    addrow.run()


def read_accel_json(input_file, start=0, device_motion=True):
    """
    Read accelerometer or deviceMotion json file.

    Parameters
    ----------
    input_file : string
        name of input accelerometer json file
    start : integer
        starting index (remove beginning)
    device_motion : Boolean
        use deviceMotion vs. accelerometer json file?

    Returns
    -------
    t : list
        time points for accelerometer data
    axyz : list of lists
        x-, y-, and z-axis accelerometer data
    gxyz : list of lists
        x-, y-, and z-axis gravity (if deviceMotion)
    uxyz : list of lists
        x-, y-, and z-axis attitude (if deviceMotion)
    rxyz : list of lists
        x-, y-, and z-axis rotationRate (if deviceMotion)
    sample_rate : float
        sample rate
    duration : float
        duration of time series

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-90f7096a-84ac-4f29-a4d1-236ef92c3d262549858224214804657.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    """
    import json

    from mhealthx.signals import compute_sample_rate

    f = open(input_file, 'r')
    json_strings = f.readlines()
    parsed_jsons = json.loads(json_strings[0])

    t = []
    ax = []
    ay = []
    az = []
    gx = []
    gy = []
    gz = []
    uw = []
    ux = []
    uy = []
    uz = []
    rx = []
    ry = []
    rz = []
    for parsed_json in parsed_jsons[start::]:
        if device_motion:
            ax.append(parsed_json['userAcceleration']['x'])
            ay.append(parsed_json['userAcceleration']['y'])
            az.append(parsed_json['userAcceleration']['z'])
            t.append(parsed_json['timestamp'])
            gx.append(parsed_json['gravity']['x'])
            gy.append(parsed_json['gravity']['y'])
            gz.append(parsed_json['gravity']['z'])
            uw.append(parsed_json['attitude']['w'])
            ux.append(parsed_json['attitude']['x'])
            uy.append(parsed_json['attitude']['y'])
            uz.append(parsed_json['attitude']['z'])
            rx.append(parsed_json['rotationRate']['x'])
            ry.append(parsed_json['rotationRate']['y'])
            rz.append(parsed_json['rotationRate']['z'])
        else:
            ax.append(parsed_json['x'])
            ay.append(parsed_json['y'])
            az.append(parsed_json['z'])
            t.append(parsed_json['timestamp'])

    axyz = [ax, ay, az]
    gxyz = [gx, gy, gz]
    uxyz = [uw, ux, uy, uz]
    rxyz = [rx, ry, rz]

    sample_rate, duration = compute_sample_rate(t)

    return t, axyz, gxyz, uxyz, rxyz, sample_rate, duration


def read_tap_json(input_file, start=0):
    """
    Read screen tap json file.

    Parameters
    ----------
    input_file : string
        name of input screen tap json file
    start : integer
        starting index (remove beginning)

    Returns
    -------
    t : list
        time points for tap data
    tx : list
        x coordinates of touch screen
    ty : list
        y coordinates of touch screen
    button : list
        buttons tapped
    sample_rate : float
        sample rate
    duration : float
        duration of time series

    Examples
    --------
    >>> from mhealthx.xio import read_tap_json
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/tapping_results.json.TappingSamples-49d2531d-dbda-4b6d-b403-f8763b8e05841011283015383434299.tmp'
    >>> start = 0
    >>> t, tx, ty, button, sample_rate, duration = read_tap_json(input_file, start)
    """
    import json
    import re

    from mhealthx.signals import compute_sample_rate

    f = open(input_file, 'r')
    json_strings = f.readlines()
    parsed_jsons = json.loads(json_strings[0])

    t = []
    tx = []
    ty = []
    button = []
    for parsed_json in parsed_jsons[start::]:
        txy = re.findall(r'\d+', parsed_json['TapCoordinate'])
        tx.append(int(txy[0]))
        ty.append(int(txy[1]))
        t.append(parsed_json['TapTimeStamp'])
        button.append(parsed_json['TappedButtonId'])

    sample_rate, duration = compute_sample_rate(t)

    return t, tx, ty, button, sample_rate, duration


def get_accel(synapse_table, row, column_name, start=0, device_motion=True,
              out_path='.', username='', password=''):
    """
    Read accelerometer json data from Synapse table row.

    Calls ::
        from mhealthx.xio import read_file_from_synapse_table
        from mhealthx.xio import read_accel_json

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    row : pandas Series or string
        row of a Synapse table converted to a Series or csv file
    column_name : string
        name of file handle column
    start : integer
        starting index (remove beginning)
    device_motion : Boolean
        use deviceMotion vs. accelerometer json file?
    out_path : string or None
        a local path in which to store downloaded files.
        If None, stores them in (~/.synapseCache)
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    ax : list
        x-axis accelerometer data
    ay : list
        y-axis accelerometer data
    az : list
        z-axis accelerometer data
    t : list
        time points for accelerometer data
    sample_rate : float
        sample rate
    duration : float
        duration of time series
    row : pandas Series
        same as passed in: row of a Synapse table as a file or Series
    file_path : string
        path to accelerometer file

    Examples
    --------
    >>> from mhealthx.xio import extract_synapse_rows, read_file_from_synapse_table, get_accel
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590866'
    >>> row_series, row_files = extract_synapse_rows(synapse_table, save_path='.', limit=3, username='', password='')
    >>> column_name = 'deviceMotion_walking_outbound.json.items'
    >>> device_motion = True
    >>> start = 150
    >>> out_path = None
    >>> username = ''
    >>> password = ''
    >>> for i in range(1):
    >>>     row = row_series[i]
    >>>     row, filepath = read_file_from_synapse_table(synapse_table, row,
    >>>         column_name, out_path, username, password)
    >>>     print(row)
    >>>     ax, ay, az, t, sample_rate, duration, row, file_path = get_accel(synapse_table,
    >>>                                       row, column_name,
    >>>                                       start, device_motion,
    >>>                                       out_path, username, password)

    """
    from mhealthx.xio import read_file_from_synapse_table, read_accel_json

    # Load row data and accelerometer json file (full path):
    row, file_path = read_file_from_synapse_table(synapse_table, row,
                                                  column_name, out_path,
                                                  username, password)
    # Read accelerometer json file:
    t, axyz, gxyz, uxyz, rxyz, sample_rate, \
    duration = read_accel_json(file_path, start, device_motion)

    ax, ay, az = axyz

    return ax, ay, az, t, sample_rate, duration, row, file_path


def get_tap(synapse_table, row, column_name, start=0,
            out_path='.', username='', password=''):
    """
    Read screen tapping json data from Synapse table row.

    Calls ::
        from mhealthx.xio import read_file_from_synapse_table
        from mhealthx.xio import read_accel_json

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    row : pandas Series or string
        row of a Synapse table converted to a Series or csv file
    column_name : string
        name of file handle column
    start : integer
        starting index (remove beginning)
    out_path : string or None
        a local path in which to store downloaded files.
        If None, stores them in (~/.synapseCache)
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    tx : list
        x-axis screen tap data
    ty : list
        y-axis screen tap data
    t : list
        time points for accelerometer data
    sample_rate : float
        sample rate
    duration : float
        duration of time series
    row : pandas Series
        same as passed in: row of a Synapse table as a file or Series
    file_path : string
        path to accelerometer file

    Examples
    --------
    >>> from mhealthx.xio import extract_synapse_rows, read_file_from_synapse_table, get_tap
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590866'
    >>> row_series, row_files = extract_synapse_rows(synapse_table, save_path='.', limit=3, username='', password='')
    >>> column_name = 'deviceMotion_walking_outbound.json.items'
    >>> start = 150
    >>> out_path = None
    >>> username = ''
    >>> password = ''
    >>> for i in range(1):
    >>>     row = row_series[i]
    >>>     row, filepath = read_file_from_synapse_table(synapse_table, row,
    >>>         column_name, out_path, username, password)
    >>>     print(row)
    >>>     tx, ty, t, sample_rate, duration, row, file_path = get_tap(synapse_table,
    >>>                                       row, column_name,
    >>>                                       start, out_path, username, password)

    """
    from mhealthx.xio import read_file_from_synapse_table, read_tap_json

    # Load row data and accelerometer json file (full path):
    row, file_path = read_file_from_synapse_table(synapse_table, row,
                                                  column_name, out_path,
                                                  username, password)
    # Read accelerometer json file:
    t, tx, ty, button, sample_rate, duration = read_tap_json(file_path, start)

    return tx, ty, t, sample_rate, duration, row, file_path


def get_convert_audio(synapse_table, row, column_name,
                      convert_file_append='', convert_command='ffmpeg',
                      convert_input_args='-y -i', convert_output_args='-ac 2',
                      out_path='.', username='', password=''):
    """
    Read data from a row of a Synapse table and convert audio file.

    Calls ::
        from mhealthx.xio import read_file_from_synapse_table
        from mhealthx.xio import convert_audio_file

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
    out_path : string or None
        a local path in which to store downloaded files.
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    row : pandas Series
        same as passed in: row of a Synapse table as a file or Series
    new_file : string
        full path to the converted file

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
    >>>     row, new_file = get_convert_audio(synapse_table,
    >>>                                       row, column_name,
    >>>                                       convert_file_append,
    >>>                                       convert_command,
    >>>                                       convert_input_args,
    >>>                                       convert_output_args,
    >>>                                       out_path, username, password)

    """
    from mhealthx.xio import read_file_from_synapse_table, convert_audio_file

    row, file_path = read_file_from_synapse_table(synapse_table, row,
                                                  column_name, out_path,
                                                  username, password)
    if convert_file_append:
        renamed_file = file_path + convert_file_append
        new_file = convert_audio_file(old_file=file_path,
                                      new_file=renamed_file,
                                      command=convert_command,
                                      input_args=convert_input_args,
                                      output_args=convert_output_args)
    else:
        new_file = None

    return row, new_file


def convert_audio_file(old_file, new_file, command='ffmpeg',
                       input_args='-i', output_args='-ac 2'):
    """
    Convert audio file to new format.

    Parameters
    ----------
    old_file : string
        full path to the input file
    new_file : string
        full path to the output file
    command : string
        executable command without arguments
    input_args : string
        arguments preceding input file name in command
    output_args : string
        arguments preceding output file name in command

    Returns
    -------
    new_file : string
        full path to the output file

    Examples
    --------
    >>> from mhealthx.xio import convert_audio_file
    >>> old_file = '/Users/arno/mhealthx_cache/mhealthx/feature_files/test.m4a'
    >>> new_file = 'test.wav'
    >>> command = 'ffmpeg'
    >>> input_args = '-y -i'
    >>> output_args = '-ac 2'
    >>> new_file = convert_audio_file(old_file, new_file, command, input_args, output_args)

    """
    import os
    from nipype.interfaces.base import CommandLine

    if not os.path.isfile(old_file):
        raise IOError("{0} does not exist.".format(old_file))
        new_file = None
    else:
        input_args = ' '.join([input_args, old_file, output_args, new_file])
        try:
            # Nipype command line wrapper:
            cli = CommandLine(command = command)
            cli.inputs.args = input_args
            cli.cmdline
            cli.run()
        except:
            print("'{0} {1}' unsuccessful".format(command, input_args))
            new_file = None

    return new_file


def write_wav(data, file_stem, file_append,
              sample_rate=44100, amplitude=32700):
    """
    Convert a list or array of numbers to a .wav format audio file.

    After: http://blog.acipo.com/wave-generation-in-python/
    and    https://gist.github.com/Pretz/1773870
    and    http://codingmess.blogspot.com/2008/07/
                  how-to-make-simple-wav-file-with-python.html

    Parameters
    ----------
    data : list or array of floats or integers
        input data to convert to audio file
    file_stem : string
        stem of file name of output audio file (including absolute path)
    file_append : string
        append string to file_stem for full output audio file path and name
    sample_rate : integer
        number of desired samples per second for audio file
    amplitude : integer
        maximum amplitude for audio file (32700 is within signed short)

    Returns
    -------
    wav_file : string
        name of output .wav audio file

    Examples
    --------
    >>> from mhealthx.xio import write_wav
    >>> import numpy as np
    >>> from scipy.signal import resample
    >>> file_stem = '/desk/temp'
    >>> file_append = 'write_wav.wav'
    >>> sample_rate = 44100
    >>> amplitude = 32700
    >>> data = np.random.random(500000)
    >>> data /= np.max(np.abs(data))
    >>> #data = resample(data, sample_rate/framerate)
    >>> wav_file = write_wav(data, file_stem, file_append, sample_rate, amplitude)
    """
    import os
    import numpy as np
    import wave
    import struct

    wav_file = file_stem + file_append
    wavfile = wave.open(wav_file, "w")
    nchannels = 1
    sampwidth = 2
    framerate = sample_rate
    nframes = len(data)
    comptype = "NONE"
    compname = "not compressed"
    wavfile.setparams((nchannels,
                       sampwidth,
                       framerate,
                       nframes,
                       comptype,
                       compname))

    data = np.asarray(data)
    data /= np.max(np.abs(data))
    data *= amplitude
    data = np.round(data)
    for x in data:
        value = struct.pack('i', x)
        wavfile.writeframesraw(value)

    wavfile.writeframes('')
    wavfile.close()

    if not os.path.isfile(wav_file):
        raise IOError("{0} has not been written.".format(filename))

    return wav_file


# ============================================================================
if __name__ == '__main__':

    pass