#!/usr/bin/env python
"""
Input/output functions to read and write Synapse tables.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def extract_rows(synapse_table, save_path=None, limit=None,
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
    row_dataframes : list of pandas DataFrames
        each row of a Synapse table converted to a dataframe
    row_files: list of strings
        file names corresponding to each of the row_dataframes

    Examples
    --------
    >>> from mhealthx.synapse_io import extract_rows
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> save_path = '.'
    >>> limit = 3
    >>> username = ''
    >>> password = ''
    >>> row_dataframes, row_files = extract_rows(synapse_table, save_path, limit, username='', password='')

    """
    import os
    import pandas as pd
    import synapseclient

    if not synapse_table:
        row_dataframes = None
        row_files = None
    else:
        try:
            # Log in to Synapse:
            syn = synapseclient.Synapse()
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

            headers = {header['name']:i for i, header
                       in enumerate(results.headers)}

            row_dataframes = []
            row_files = []
            for irow, row in enumerate(results):
                row_map = {col:row[i] for col,i in headers.iteritems()}
                columns = row_map.keys()
                values = [unicode(x) for x in row_map.values()]
                df = pd.DataFrame(values, columns)
                row_dataframe = df.transpose()
                row_dataframes.append(row_dataframe)
                if save_path:
                    csv_file = "row{0}.csv".format(irow)
                    csv_file = os.path.join(save_path, csv_file)
                    row_dataframe.to_csv(csv_file)
                    row_files.append(csv_file)
        except:
            row_dataframes = None
            row_files = None

    return row_dataframes, row_files


def read_files_from_row(synapse_table, row, column_name,
                        out_path='.', username='', password=''):
    """
    Read data from a row of a Synapse table.

    Parameters
    ----------
    synapse_table : string or Schema
        a synapse ID or synapse table Schema object
    row : pandas DataFrame or string
        row of a Synapse table converted to a dataframe or csv file
    column_name : string
        name of file handle column
    out_path : string
        a local path in which to store downloaded files. If None, stores them in (~/.synapseCache)
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    row : pandas DataFrame
        same as passed in: row of a Synapse table as a file or dataframe
    filepath : string
        downloaded file (full path)

    Examples
    --------
    >>> from mhealthx.synapse_io import extract_rows, read_files_from_row
    >>> import synapseclient
    >>> syn = synapseclient.Synapse()
    >>> syn.login()
    >>> synapse_table = 'syn4590865'
    >>> save_path = '.'
    >>> limit = 3
    >>> username = ''
    >>> password = ''
    >>> row_dataframes, row_files = extract_rows(synapse_table, save_path, limit, username='', password='')
    >>> column_name = 'audio_audio.m4a' #, 'audio_countdown.m4a']
    >>> out_path = '.'
    >>> for i in range(3):
    >>>     row = row_dataframes[i]
    >>>     row, filepath = read_files_from_row(synapse_table, row, column_name, out_path, username, password)
    >>>     print(row)

    """
    import pandas as pd
    import synapseclient

    if synapse_table is None or row is None:
        row = None
        filepath = None
    else:
        if type(row) == pd.DataFrame:
            pass
        elif type(row) == str:
            row = pd.read_csv(row)
        else:
            raise Warning("row should be a pandas DataFrame or a file string")

        # Log in to Synapse:
        syn = synapseclient.Synapse()
        if username and password:
            syn.login(username, password)
        else:
            syn.login()

        # Try to download file with column_name in row:
        try:
            fileinfo = syn.downloadTableFile(synapse_table,
                                rowId=row['ROW_ID'][0],
                                versionNumber=row['ROW_VERSION'][0],
                                column=column_name,
                                downloadLocation=out_path)
            filepath = fileinfo['path']
        except:
            row = None
            filepath = None

    return row, filepath








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
    >>> from mhealthx.synapse_io import copy_synapse_table
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
    >>> from mhealthx.synapse_io import read_synapse_table_files, write_synapse_table
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
    >>> from mhealthx.synapse_io import feature_file_to_synapse_table
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
