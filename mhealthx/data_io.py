#!/usr/bin/env python
"""
Input/output functions to read and write Synapse tables.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def convert_audio_file(old_file, file_append, command='ffmpeg',
                       input_args='-i', output_args='-ac 2'):
    """
    Convert audio file to new format.

    Parameters
    ----------
    old_file : list of strings
        full path to the input files
    file_append : string
        append to each file name to indicate output file format (e.g., '.wav')
    command : string
        executable command without arguments
    input_args : string
        arguments preceding input file name in command
    output_args : string
        arguments preceding output file name in command

    Returns
    -------
    converted_file : string
        full path to the converted file

    Examples
    --------
    >>> from mhealthx.unused import convert_audio_file
    >>> old_file = '/Users/arno/mhealthx_working/mHealthX/phonation_files/test.m4a'
    >>> file_append = '.wav'
    >>> command = '/home/arno/software/audio/ffmpeg/ffmpeg'
    >>> input_args = '-i'
    >>> output_args = '-ac 2'
    >>> converted_file = convert_audio_file(old_file, file_append, command, input_args, output_args)

    """
    import os
    from nipype.interfaces.base import CommandLine

    if not os.path.exists(old_file):
        raise(IOError(old_file + " not found"))
    else:
        # Don't convert file if file already has correct append:
        if old_file.endswith(file_append):
            converted_file = old_file
        # Convert file to new format:
        else:
            output_file = old_file + file_append
            if os.path.exists(output_file):
                converted_file = output_file
            else:
                # Nipype command line wrapper:
                cli = CommandLine(command = command)
                cli.inputs.args = ' '.join([input_args, old_file,
                                            output_args, output_file])
                cli.cmdline
                cli.run()

                if not os.path.exists(output_file):
                    raise(IOError(output_file + " not found"))
                else:
                    converted_file = output_file

    return converted_file


def extract_rows(synapse_table, limit=None, username='', password=''):
    """
    Extract rows from a Synapse table.

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    limit : integer or None
        limit to number of rows returned by the query
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    row_as_map_list : list of dicts
        multiple rows of a table converted to a map with column names as keys

    Examples
    --------
    >>> from mhealthx.data_io import extract_rows
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> limit = 3
    >>> username = ''
    >>> password = ''
    >>> row_as_map_list = extract_rows(synapse_table, limit, username='', password='')

    """
    import synapseclient

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    if limit:
        results = syn.tableQuery('select * from {0} limit {1}'.
                                 format(synapse_table, limit))
    else:
        results = syn.tableQuery('select * from {0}'.
                                 format(synapse_table))

    headers = {header['name']:i for i,header in enumerate(results.headers)}

    row_as_map_list = []
    for row in results:
         row_as_map_list.append({col:row[i] for col,i in headers.iteritems()})

    return row_as_map_list


def read_files_from_row(synapse_table, row_as_map, column_name,
                        out_path='.', username='', password=''):
    """
    Read data from a row of a synapse table.

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    row_as_map : dict
        a row of a table converted to a map with column names as keys
    column_name : strings
        name of file handle column
    out_path : string
        a local path in which to store downloaded files. If None, stores them in (~/.synapseCache)

    Returns
    -------
    row_as_map : dict
        same as passed in: a row of a table converted to a map with column names as keys
    filepath_map : dict
        a map from file handle ID to a path on the local file system to the downloaded file
    filepath : string
        downloaded file (full path)

    Examples
    --------
    >>> from mhealthx.data_io import read_files_from_row
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> table_id = 'syn4590865'
    >>> results = syn.tableQuery('select * from {0} limit 10'.format(table_id))
    >>> headers = {header['name']:i for i,header in enumerate(results.headers)}
    >>> column_name = 'audio_audio.m4a' #, 'audio_countdown.m4a']
    >>> out_path = '.'
    >>> username = ''
    >>> password = ''
    >>>
    >>> for row in results:
    >>>     row_as_map = {col:row[i] for col,i in headers.iteritems()}
    >>>     row_as_map, filepath_map, filepath = read_files_from_row(table_id, row_as_map, column_name, out_path, username, password)
    >>>     print('\nRecordID: {0}\n {1}\n'.format(row_as_map['recordId'], filepath_map))

    """
    import synapseclient

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    filepath_map = {}
    fileinfo = syn.downloadTableFile(synapse_table,
                                     rowId=row_as_map['ROW_ID'],
                                     versionNumber=row_as_map['ROW_VERSION'],
                                     column=column_name,
                                     downloadLocation=out_path)
    filepath_map[row_as_map[column_name]] = fileinfo['path']

    filepath = fileinfo['path']

    return row_as_map, filepath_map, filepath


def copy_synapse_table(synapse_table_id, synapse_project_id, table_name='',
                       remove_columns=[], username='', password=''):
    """
    Copy Synapse table to another Synapse project.

    Parameters
    ----------
    synapse_table_id : string
        Synapse ID for table to copy
    synapse_project_id : string
        copy table to project with this Synapse ID
    table_name : string
        schema name of table
    remove_columns : list of strings
        column headers for columns to be removed
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    table_data : Pandas DataFrame
        Synapse table contents
    table_name : string
        schema name of table
    synapse_project_id : string
        Synapse ID for project within which table is to be written

    Examples
    --------
    >>> from mhealthx.data_io import copy_synapse_table
    >>> synapse_table_id = 'syn4590865'
    >>> synapse_project_id = 'syn4899451'
    >>> table_name = 'Copy of ' + synapse_table_id
    >>> remove_columns = ['audio_audio.m4a', 'audio_countdown.m4a']
    >>> username = ''
    >>> password = ''
    >>> table_data, table_name, synapse_project_id = copy_synapse_table(synapse_table_id, synapse_project_id, table_name, remove_columns, username, password)

    """
    import synapseclient
    from synapseclient import Schema
    from synapseclient.table import Table, as_table_columns

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Download Synapse table as a dataframe:
    results = syn.tableQuery("select * from {0}".format(synapse_table_id))
    table_data = results.asDataFrame()

    # Remove specified columns:
    if remove_columns:
        for remove_column in remove_columns:
            del table_data[remove_column]

    # Upload to Synapse table:
    table_data.index = range(table_data.shape[0])
    schema = Schema(name=table_name, columns=as_table_columns(table_data),
                    parent=synapse_project_id,
                    includeRowIdAndRowVersion=False)
    table = syn.store(Table(schema, table_data))

    return table_data, table_name, synapse_project_id


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
    >>> from mhealthx.data_io import read_synapse_table_files, write_synapse_table
    >>> in_synapse_table_id = 'syn4590865'
    >>> synapse_project_id = 'syn4899451'
    >>> column_names = []
    >>> download_limit = None
    >>> out_path = '.'
    >>> username = ''
    >>> password = ''
    >>> table_data, files = read_synapse_table_files(in_synapse_table_id, column_names, download_limit, out_path, username, password)
    >>> table_name = 'Contents of ' + in_synapse_table_id
    >>> write_synapse_table(table_data, synapse_project_id, table_name, username, password)

    """
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    table_data.index = range(table_data.shape[0])

    schema = Schema(name=table_name, columns=as_table_columns(table_data),
                    parent=synapse_project_id, includeRowIdAndRowVersion=False)

    syn.store(Table(schema, table_data))


def feature_file_to_synapse_table(feature_file, raw_feature_file,
                                  source_file_id, provenance_activity_id,
                                  command, command_line,
                                  synapse_table_id, username='', password=''):
    """
    Upload files and file handle IDs to Synapse.

    Parameters
    ----------
    feature_file : string
        path to file to upload to Synapse
    raw_feature_file : string
        path to file to upload to Synapse
    source_file_id : string
        Synapse file handle ID to source file used to generate features
    provenance_activity_id : string
        Synapse provenance activity ID
    command : string
        name of command run to generate raw feature file
    command_line : string
        full command line run to generate raw feature file
    synapse_table_id : string
        Synapse table ID for table to store file handle IDs, etc.
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Examples
    --------
    >>> from mhealthx.data_io import feature_file_to_synapse_table
    >>> feature_file = '/Users/arno/Local/wav/test1.wav'
    >>> raw_feature_file = '/Users/arno/Local/wav/test1.wav'
    >>> source_file_id = ''
    >>> provenance_activity_id = ''
    >>> command_line = 'SMILExtract -C blah -I blah -O blah'
    >>> synapse_table_id = 'syn4899451'
    >>> username = ''
    >>> password = ''
    >>> feature_file_to_synapse_table(feature_file, raw_feature_file, source_file_id, provenance_activity_id, command_line, synapse_table_id, username, password)

    """
    import synapseclient
    from synapseclient.table import Table

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Store feature and raw feature files and get file handle IDs:
    file_handle = syn._chunkedUploadFile(feature_file)
    file_id = file_handle['id']
    raw_file_handle = syn._chunkedUploadFile(raw_feature_file)
    raw_file_id = raw_file_handle['id']

    # Add new row to Synapse table:
    new_rows = [[file_id, raw_file_id, source_file_id,
                 provenance_activity_id, command, command_line]]
    schema = syn.get(synapse_table_id)
    table = syn.store(Table(schema, new_rows))

    return synapse_table_id


def arff_to_csv(arff_file, csv_file):
    """
    Convert an arff file to csv format.

    Column headers include lines that start with '@attribute ',
    include 'numeric', and whose intervening string is not exception_string.
    The function raises an error if the number of resulting columns does
    not equal the number of numeric values.

    Example input: arff output from openSMILE's SMILExtract command

    Adapted some formatting from:
    http://biggyani.blogspot.com/2014/08/
    converting-back-and-forth-between-weka.html

    Parameters
    ----------
    arff_file : string
        arff file (full path)
    csv_file : string
        csv file (full path)

    Returns
    -------
    csv_file : string
        csv file (full path)

    Examples
    --------
    >>> from mhealthx.data_io import arff_to_csv
    >>> arff_file = '/Users/arno/csv/test1.csv'
    >>> csv_file = 'test.csv'
    >>> csv_file = arff_to_csv(arff_file, csv_file)

    """
    import os

    # String not included as a header:
    exception_string = 'class'
    # Remove items from the left and right in the '@data' row:
    data_from_left = 1
    data_from_right = 1

    # Check to make sure arff_file exists:
    if type(arff_file) != str or not os.path.isfile(arff_file):
        raise IOError("The arff file {0} does not exist.".format(arff_file))

    # Open arff_file:
    with open(arff_file, 'r') as fid:
        lines = fid.readlines()

    # Loop through lines of the arff file:
    cols = []
    first_numeric = False
    last_numeric = False
    for iline, line in enumerate(lines):
        if '@data' in line:
            break
        else:

            # If line starts with '@attribute ' and contains 'numeric',
            # append intervening string as a column name, and
            # store index as first line of column names:
            if line.startswith('@attribute ') and 'numeric' in line:
                if '{' in line:
                    interstring = line[11:line.index('{') - 1]
                else:
                    interstring = line[11:line.index('numeric') - 1]

                # If intervening string between '@attribute ' and 'numeric'
                # is not the exception_string, include as a column header:
                if interstring != exception_string:
                    cols.append(interstring)
                    if not first_numeric:
                        first_numeric = True

            # Else break if past first line with '@attribute ' and 'numeric':
            elif first_numeric:
                break

    # Remove left and right (first and last) data items:
    data = lines[len(lines)-1].split(',')
    data = data[data_from_left:-data_from_right]

    if len(data) != len(cols):
        raise Exception('The arff file does not conform to expected format.')

    # Write csv file:
    headers = ",".join(cols)
    data_string = ', '.join(data) + '\n'
    if not csv_file:
        csv_file = arff_file + '.csv'
    with open(csv_file, 'w') as fout:
        fout.write(headers)
        fout.write('\n')
        fout.writelines(data_string)

    return csv_file


def dataframes_to_csv_file(dataframes, csv_file):
    """
    Concatenate multiple pandas DataFrames with the same column names,
    and store as a csv table.

    Parameters
    ----------
    dataframes : list of pandas DataFrames
        each dataframe has the same column names
    csv_file : string
        path of table file

    Returns
    -------
    table_data : Pandas DataFrame
        output table data
    csv_file : string
        path of table file

    Examples
    --------
    >>> import pandas as pd
    >>> from mhealthx.io_data import dataframes_to_csv_file
    >>> df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
    >>>                     'B': ['B0', 'B1', 'B2', 'B3'],
    >>>                     'C': ['C0', 'C1', 'C2', 'C3'],
    >>>                     'D': ['D0', 'D1', 'D2', 'D3']},
    >>>                    index=[0, 1, 2, 3])
    >>> df2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
    >>>                     'B': ['B4', 'B5', 'B6', 'B7'],
    >>>                     'C': ['C4', 'C5', 'C6', 'C7'],
    >>>                     'D': ['D4', 'D5', 'D6', 'D7']},
    >>>                     index=[0, 1, 2, 3])
    >>> dataframes = [df1, df2]
    >>> csv_file = './test.csv'
    >>> table_data, csv_file = dataframes_to_csv_file(dataframes, csv_file)
    """
    import pandas as pd

    # Raise an error if tables are not pandas DataFrames:
    if not type(dataframes[0]) == pd.DataFrame:
        raise IOError("'dataframes' should contain pandas DataFrames.")

    # Concatenate DataFrames, increasing the number of rows:
    table_data = pd.concat(dataframes, ignore_index=True)

    # Store as csv file:
    table_data.to_csv(csv_file, index=False)

    return table_data, csv_file


# ============================================================================
# Run above functions to convert all voice files to wav and upload to Synapse:
# ============================================================================
if __name__ == '__main__':

    pass
    # # Setup:
    # synapse_table_id = 'syn4590865'
    # target_synapse_project_id = 'syn4899451'
    # username = ''
    # password = ''
    # column_name = 'audio_audio.wav'
    # download_limit = 3 # Test with first 3 rows or None for all rows
    # out_path = '.'
    # ffmpeg = '/home/arno/software/audio/ffmpeg/ffmpeg'
    # table_name = 'mPower phonation wav files and file handle IDs'
    # #table_name = 'mPower countdown wav files and file handle IDs'
    #
    # # Download files:
    # table_data, files = read_synapse_table_files(synapse_table_id,
    #                                              column_name, download_limit,
    #                                              out_path,
    #                                              username, password)
    #
    # # Upload wav files and file handle IDs:
    # files_to_synapse_table(files, target_synapse_project_id,
    #                                 table_name, username, password)
