#!/usr/bin/env python
"""
Input/output functions to read, write, and modify files and Synapse tables.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def read_synapse_table_files(synapse_table_ID,
                             column_name='', select_rows=[], output_path='.',
                             username='', password=''):
    """
    Read data from a Synapse table. If column_name specified, download files.

    Parameters
    ----------
    synapse_table_ID : string
        Synapse ID for table
    column_name : string
        column header for fileIDs in Synapse table (if wish to download files)
    select_rows : list
        row indices, if retrieving column_name files (empty means all rows)
    output_path : string
        output path to store column_name files
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    dataframe : Pandas DataFrame
        Synapse table contents
    files : list of strings
        files from Synapse table (full paths to downloaded files)

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table_files
    >>> synapse_table_ID = 'syn4590865'
    >>> column_name = 'audio_audio.m4a'
    >>> select_rows = range(3)  # [] for all rows
    >>> output_path = '.'
    >>> username = ''
    >>> password = ''
    >>> dataframe, files = read_synapse_table_files(synapse_table_ID, column_name, select_rows, output_path, username, password)

    """
    import synapseclient

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Download Synapse table schema and dataframe:
    schema = syn.get(synapse_table_ID)
    results = syn.tableQuery("select * from {0}".format(synapse_table_ID))
    dataframe = results.asDataFrame()
    files = []

    # Download Synapse files for fileIDs in specified table column:
    if column_name:
        if not select_rows:
            select_rows = range(dataframe.shape[0])
        for rowID in select_rows:
            fileinfo = syn.downloadTableFile(schema,
                                             rowId=rowID,
                                             versionNumber=0,
                                             column=column_name,
                                             downloadLocation=output_path)
            if fileinfo:
                files.append(fileinfo['path'])
            else:
                files.append('')

    return dataframe, files


def write_synapse_table(dataframe, project_synID, schema_name='',
                        username='', password=''):
    """
    Write data to a Synapse table.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Synapse table contents
    project_synID : string
        Synapse ID for project within which table is to be written
    schema_name : string
        schema name of table
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table, write_synapse_table
    >>> input_synapse_table_ID = 'syn4590865'
    >>> project_synID = 'syn4899451'
    >>> dataframe = read_synapse_table(input_synapse_table_ID, username, password)
    >>> schema_name = 'Contents of ' + input_synapse_table_ID
    >>> username = ''
    >>> password = ''
    >>> write_synapse_table(dataframe, project_synID, schema_name, username, password)

    """
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    dataframe.index = range(dataframe.shape[0])

    schema = Schema(name=schema_name, columns=as_table_columns(dataframe),
                    parent=project_synID, includeRowIdAndRowVersion=False)

    syn.store(Table(schema, dataframe))


def upload_files_handles_to_synapse(input_files, project_synID,
                                    schema_name='', username='', password=''):
    """
    Upload files and file handle IDs to Synapse.

    Parameters
    ----------
    input_files : list of strings
        paths to files to upload to Synapse
    project_synID : string
        Synapse ID for project within which table is to be written
    schema_name : string
        schema name of table
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Examples
    --------
    >>> from mhealthx.io_data import upload_files_handles_to_synapse
    >>> input_files = ['/Users/arno/Local/wav/test1.wav', '/Users/arno/Local/wav/test2.wav']
    >>> project_synID = 'syn4899451'
    >>> schema_name = 'Test to store files and file handle IDs'
    >>> username = ''
    >>> password = ''
    >>> upload_files_handles_to_synapse(input_files, project_synID, schema_name, username, password)

    """
    import os
    import synapseclient
    from synapseclient import Schema
    from synapseclient.table import Column, RowSet, Row

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Store file handle IDs:
    files_handles = []
    for input_file in input_files:
        file_handle = syn._chunkedUploadFile(input_file)
        files_handles.append([file_handle['id']])

    # Upload files and file handle IDs:
    cols = [Column(name='fileID', columnType='FILEHANDLEID')]
    schema = syn.store(Schema(name=schema_name, columns=cols, parent=project_synID))
    syn.store(RowSet(columns=cols, schema=schema,
                     rows=[Row(r) for r in files_handles]))


def append_file_names(input_files, file_append):
    """
    Copy each file with an append to its file name.

    Parameters
    ----------
    input_files : list of strings
        full path to the input files
    file_append : string
        append to each file name

    Returns
    -------
    output_files : list of strings
        each string is the full path to a renamed file

    Examples
    --------
    >>> from mhealthx.io_data import append_file_names
    >>> input_files = ['/Users/arno/mhealthx_working/mHealthX/phonation_files/test.tmp']
    >>> file_append = '.m4a'
    >>> output_files = append_file_names(input_files, file_append)

    """
    import os
    from shutil import copyfile

    output_files = []

    # Loop through input files:
    for input_file in input_files:
        if not os.path.exists(input_file):
            raise(IOError(input_file + " not found"))
        else:
            # Don't copy file if file already has correct append:
            if input_file.endswith(file_append):
                output_files.append(input_file)
            # Copy to a new file with appended file name:
            else:
                output_file = input_file + file_append
                copyfile(input_file, output_file)
                if not os.path.exists(output_file):
                    raise(IOError(output_file + " not found"))
                else:
                    output_files.append(output_file)

    return output_files


def convert_audio_files(input_files, file_append, command='ffmpeg',
                        input_args='-i', output_args='-ac 2'):
    """
    Convert audio files to new format.

    Calls python-audiotranscode (and faad2)

    Parameters
    ----------
    input_files : list of strings
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
    output_files : list of strings
        each string is the full path to a renamed file

    Examples
    --------
    >>> from mhealthx.io_data import convert_audio_files
    >>> input_files = ['/Users/arno/mhealthx_working/mHealthX/phonation_files/test.m4a']
    >>> file_append = '.wav'
    >>> command = '/home/arno/software/audio/ffmpeg/ffmpeg'
    >>> input_args = '-i'
    >>> output_args = '-ac 2'
    >>> output_files = convert_audio_files(input_files, file_append, command, input_args, output_args)

    """
    import os
    from nipype.interfaces.base import CommandLine

    output_files = []

    # Loop through input files:
    for input_file in input_files:
        if not os.path.exists(input_file):
            raise(IOError(input_file + " not found"))
        else:
            # Don't convert file if file already has correct append:
            if input_file.endswith(file_append):
                output_files.append(input_file)
            # Convert file to new format:
            else:
                output_file = input_file + file_append
                if os.path.exists(output_file):
                    output_files.append(output_file)
                else:
                    # Nipype command line wrapper:
                    cli = CommandLine(command = command)
                    cli.inputs.args = ' '.join([input_args, input_file,
                                                output_args, output_file])
                    cli.cmdline
                    cli.run()

                    if not os.path.exists(output_file):
                        raise(IOError(output_file + " not found"))
                    else:
                        output_files.append(output_file)

    return output_files


# ============================================================================
# Run above functions to convert all voice files to wav and upload to Synapse:
# ============================================================================
if __name__ == '__main__':

    # Setup:
    synapse_table_ID = 'syn4590865'
    target_project_synID = 'syn4899451'
    username = ''
    password = ''
    column_name = 'audio_audio.m4a'
    select_rows = range(3) #[]  # Test with first 3 rows: range(3)
    output_path = '.'
    ffmpeg = '/home/arno/software/audio/ffmpeg/ffmpeg'
    schema_name = 'mPower phonation wav files and file handle IDs'
    #schema_name = 'mPower countdown wav files and file handle IDs'

    # Download files:
    dataframe, files = read_synapse_table_files(synapse_table_ID, column_name,
                                                select_rows, output_path,
                                                username, password)

    # Rename files with .m4a append (copy):
    file_append1 = '.m4a'
    renamed_files = append_file_names(files, file_append1)

    # Convert from m4a to wav:
    file_append2 = '.wav'
    input_args = '-i'
    output_args = '-ac 2'
    output_files = convert_audio_files(renamed_files, file_append2, ffmpeg,
                                       input_args, output_args)

    # Upload wav files and file handle IDs:
    upload_files_handles_to_synapse(output_files, target_project_synID,
                                    schema_name, username, password)
