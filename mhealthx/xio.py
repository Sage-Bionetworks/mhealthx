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
    syn = synapseclient.Synapse(skip_checks=True)
    if username and password:
        syn.login(username, password, silent=True)
    else:
        syn.login(silent=True)

    # Synapse table query:
    if limit:
        limit_string = 'limit {0}'.format(limit)
    else:
        limit_string = ''
    try:
        results = syn.tableQuery('select * from {0} {1}'.
                                 format(synapse_table, limit_string))
    except IOError as e:
        import traceback; traceback.print_exc()
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
                    import traceback; traceback.print_exc()
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
    syn = synapseclient.Synapse(skip_checks=True)
    if username and password:
        syn.login(username, password, silent=True)
    else:
        syn.login(silent=True)

    # Try to download file with column_name in row:
    try:
        if not out_path:
            out_path='./row{0}_v{1}_{2}'.format(row['ROW_ID'],
                                                row['ROW_VERSION'],
                                                row['recordId'])
        fileinfo = syn.downloadTableFile(synapse_table,
                            rowId=row['ROW_ID'],
                            versionNumber=row['ROW_VERSION'],
                            column=column_name,
                            downloadLocation=out_path)
        filepath = fileinfo['path']
    except IOError as e:
        import traceback; traceback.print_exc()
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
    wxyz : list of lists
        w, x, y, z attitude quaternion (if deviceMotion)
    rxyz : list of lists
        x-, y-, and z-axis rotationRate (if deviceMotion)
    sample_rate : float
        sample rate
    duration : float
        duration of time series

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-90f7096a-84ac-4f29-a4d1-236ef92c3d262549858224214804657.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> t, axyz, gxyz, wxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    """
    import json

    from mhealthx.signals import compute_sample_rate, gravity_min_mse

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
    wxyz = [uw, ux, uy, uz]
    rxyz = [rx, ry, rz]

    sample_rate, duration = compute_sample_rate(t)

    return t, axyz, gxyz, wxyz, rxyz, sample_rate, duration


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
    t : list
        time points for accelerometer data
    ax : list
        x-axis acceleration
    ay : list
        y-axis acceleration
    az : list
        z-axis acceleration
    gx : list
        x-axis gravity acceleration
    gy : list
        y-axis gravity acceleration
    gz : list
        z-axis gravity acceleration
    rx : list
        x-axis rotationRate
    ry : list
        y-axis rotationRate
    rz : list
        z-axis rotationRate
    uw : list
        w of attitude quaternion
    ux : list
        x of attitude quaternion
    uy : list
        y of attitude quaternion
    uz : list
        z of attitude quaternion
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
    >>>     t, ax, ay, az, gx, gy, gz, rx, ry, rz, uw, ux, uy, uz, sample_rate, duration, row, file_path = get_accel(synapse_table,
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
    t, axyz, gxyz, wxyz, rxyz, sample_rate, \
    duration, = read_accel_json(file_path, start, device_motion)

    ax, ay, az = axyz
    gx, gy, gz = gxyz
    rx, ry, rz = rxyz
    uw, ux, uy, uz = wxyz

    return t, ax, ay, az, gx, gy, gz, rx, ry, rz, uw, ux, uy, uz, \
           sample_rate, duration, row, file_path


def get_tap(synapse_table, row, column_name, start=0,
            out_path='.', username='', password=''):
    """
    Read screen tapping json data from Synapse table row.

    Calls ::
        from mhealthx.xio import read_file_from_synapse_table
        from mhealthx.xio import read_tap_json

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
            import traceback; traceback.print_exc()
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


def concatenate_tables_vertically(tables, output_csv_file=None):
    """
    Vertically concatenate multiple table files or pandas DataFrames
    with the same column names and store as a csv table.

    Parameters
    ----------
    tables : list of table files or pandas DataFrames
        each table or dataframe has the same column names
    output_csv_file : string or None
        output table file (full path)

    Returns
    -------
    table_data : Pandas DataFrame
        output table data
    output_csv_file : string or None
        output table file (full path)

    Examples
    --------
    >>> import pandas as pd
    >>> from mhealthx.xio import concatenate_tables_vertically
    >>> df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
    >>>                     'B': ['B0', 'B1', 'B2', 'B3'],
    >>>                     'C': ['C0', 'C1', 'C2', 'C3']},
    >>>                    index=[0, 1, 2, 3])
    >>> df2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
    >>>                     'B': ['B4', 'B5', 'B6', 'B7'],
    >>>                     'C': ['C4', 'C5', 'C6', 'C7']},
    >>>                     index=[0, 1, 2, 3])
    >>> tables = [df1, df2]
    >>> tables = ['/Users/arno/csv/table1.csv', '/Users/arno/csv/table2.csv']
    >>> output_csv_file = None #'./test.csv'
    >>> table_data, output_csv_file = concatenate_tables_vertically(tables, output_csv_file)
    """
    import os
    import pandas as pd

    if not tables:
        table_data = None
        output_csv_file = None
    else:
        try:
            # pandas DataFrames:
            if type(tables[0]) == pd.DataFrame:
                tables_no_Nones = []
                for table in tables:
                    if table is not None and type(table) == pd.DataFrame:
                        tables_no_Nones.append(table)
                tables = tables_no_Nones
            # file strings:
            elif type(tables[0]) == str:
                tables_from_files = []
                for table in tables:
                    if os.path.isfile(table):
                        tables_from_files.append(pd.read_csv(table))
                    else:
                        raise Warning('{0} is not a file.'.format(table))
                tables = tables_from_files
            else:
                raise Warning("'tables' should contain strings or "
                              "pandas DataFrames.")

            # Vertically concatenate tables:
            table_data = pd.concat(tables, ignore_index=True)

            # Store as csv file:
            if output_csv_file:
                table_data.to_csv(output_csv_file, index=False)
        except:
            import traceback; traceback.print_exc()
            table_data = None
            output_csv_file = None

    return table_data, output_csv_file


def select_columns_from_table(table, column_headers, write_table=True,
                              output_table=''):
    """
    Select columns from table and make a new table.

    Parameters
    ----------
    table : string
    column_headers : list of strings
        headers for columns to select
    write_table : Boolean
        write output table?
    output_table : string
        output table file name

    Returns
    -------
    columns : list of lists of floats or integers
        columns of data
    output_table :  string
        output table file name

    Examples
    --------
    >>> import os
    >>> from mhealthx.xio import select_columns_from_table
    >>> path = os.environ['MHEALTHX_OUTPUT']
    >>> table = os.path.join(path, 'feature_tables',
    ...         'tap_row0_v0_9d44a388-5d7e-4271-8705-2faa66204486.csv')
    >>> column_headers = ['tapping_results.json.ButtonRectLeft',
    ...                   'accel_tapping.json.items']
    >>> write_table = True
    >>> output_table = ''
    >>> columns, output_table = select_columns_from_table(table, column_headers, write_table, output_table)

    """
    import os
    import pandas as pd

    #-------------------------------------------------------------------------
    # Load table:
    #-------------------------------------------------------------------------
    input_columns = pd.read_csv(table)

    #-------------------------------------------------------------------------
    # Construct a table from selected columns:
    #-------------------------------------------------------------------------
    columns = input_columns[column_headers]

    #-------------------------------------------------------------------------
    # Write table:
    #-------------------------------------------------------------------------
    if write_table and not columns.empty:
        if not output_table:
            output_table = os.path.join(os.getcwd(),
                                        'select_columns_from_table.csv')
        columns.to_csv(output_table, index=False)
    else:
        print('Not saving table.')

    return columns, output_table


def write_synapse_table(table_data, synapse_project_id, table_name='',
                        username='', password=''):
    """
    Write data to a Synapse table.

    Parameters
    ----------
    table_data : Pandas DataFrame
        Synapse table contents
    synapse_project_id : string
        Synapse ID for project within which table is to be written
    table_name : string
        schema name of table
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Examples
    --------
    >>> import os
    >>> import pandas as pd
    >>> from mhealthx.xio import write_synapse_table
    >>> path = os.environ['MHEALTHX_OUTPUT']
    >>> table = os.path.join(path, 'feature_tables',
    ...         'tap_row0_v0_9d44a388-5d7e-4271-8705-2faa66204486.csv')
    >>> table_data = pd.read_csv(table)
    >>> username = ''
    >>> password = ''
    >>> synapse_project_id = 'syn4899451'
    >>> table_name = 'Contents of table'
    >>> write_synapse_table(table_data, synapse_project_id, table_name, username, password)

    """
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    syn = synapseclient.Synapse(skip_checks=True)

    # Log in to Synapse:
    if username and password:
        syn.login(username, password, silent=True)
    else:
        syn.login(silent=True)

    #table_data.index = range(table_data.shape[0])

    schema = Schema(name=table_name, columns=as_table_columns(table_data),
                    parent=synapse_project_id, includeRowIdAndRowVersion=False)

    syn.store(Table(schema, table_data))


def write_columns_to_synapse_table(table, column_headers, synapse_project_id,
                                   table_name='', username='', password=''):
    """
    Select columns from a table and write data to a Synapse table.

    Parameters
    ----------
    table : string
    column_headers : list of strings
        headers for columns to select
    synapse_project_id : string
        Synapse ID for project within which table is to be written
    table_name : string
        schema name of table
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Examples
    --------
    >>> import os
    >>> from mhealthx.xio import write_columns_to_synapse_table
    >>> path = os.environ['MHEALTHX_OUTPUT']
    >>> table = os.path.join(path, 'feature_tables',
    ...         'tap_row0_v0_9d44a388-5d7e-4271-8705-2faa66204486.csv']
    >>> column_headers = ['tapping_results.json.ButtonRectLeft',
    ...                   'accel_tapping.json.items']
    >>> username = ''
    >>> password = ''
    >>> synapse_project_id = 'syn4899451'
    >>> table_name = 'Contents written to ' + synapse_table
    >>> write_columns_to_synapse_table(table, column_headers, synapse_project_id, table_name, username, password)

    """
    from mhealthx.xio import select_columns_from_table, write_synapse_table

    #-------------------------------------------------------------------------
    # Select columns:
    #-------------------------------------------------------------------------
    columns, output_table = select_columns_from_table(table, column_headers,
                                                      False, '')

    write_synapse_table(columns, synapse_project_id, table_name,
                        username, password)


# ============================================================================
if __name__ == '__main__':

    pass