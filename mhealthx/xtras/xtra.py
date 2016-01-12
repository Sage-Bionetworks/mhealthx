#!/usr/bin/env python
"""
Unused functions.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def rename_file(old_file, new_filename='', new_path='', file_append='',
                create_file=False):
    """
    Rename (and optionally copy) a file / path / file_append.

    Parameters
    ----------
    old_file : string
        old file name (full path)
    new_filename : string
        new file name (not the full path)
    new_path : string
        replacement path
    file_append : string
        append to file names
    create_file : Boolean
        copy file (or just create a string)?

    Returns
    -------
    new_filepath : string
        new file name (full path, if remove_path not set)

    Examples
    --------
    >>> from mhealthx.utils import rename_file
    >>> old_file = '/homedir/wav/test1.wav'
    >>> new_filename = ''
    >>> new_path = '.'
    >>> file_append = '.csv'
    >>> create_file = True
    >>> new_filepath = rename_file(old_file, new_filename, new_path, file_append, create_file)
    """
    import os
    from shutil import copyfile

    old_path, base_file_name = os.path.split(old_file)

    if new_filename:
        base_file_name = new_filename

    if new_path:
        new_filepath = os.path.join(new_path, base_file_name)
    else:
        new_filepath = os.path.join(old_path, base_file_name)

    if file_append:
        new_filepath = ''.join((new_filepath, file_append))

    if create_file:
        copyfile(old_file, new_filepath)

    return new_filepath


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
    >>> from mhealthx.xtra import copy_synapse_table
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
    >>> from mhealthx.xtra import feature_file_to_synapse_table
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


def arff_to_csv(arff_file, output_csv_file=None):
    """
    Convert an arff file to a row.

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
    output_csv_file : string or None
        output table file (full path)

    Returns
    -------
    row_data : Pandas Series
        output table data
    output_csv_file : string or None
        output table file (full path)

    Examples
    --------
    >>> from mhealthx.xtra import arff_to_csv
    >>> arff_file = '/Users/arno/csv/test1.csv'
    >>> output_csv_file = None #'test.csv'
    >>> row_data, output_csv_file = arff_to_csv(arff_file, output_csv_file)

    """
    import pandas as pd

    if arff_file is None:
        row_data = None
        output_csv_file = None
    else:
        try:
            # String not included as a header:
            exception_string = 'class'
            # Remove items from the left and right in the '@data' row:
            data_from_left = 1
            data_from_right = 1

            # Open arff_file:
            with open(arff_file, 'r') as fid:
                lines = fid.readlines()

            # Loop through lines of the arff file:
            columns = []
            first_numeric = False
            for iline, line in enumerate(lines):
                if '@data' in line:
                    break
                else:

                    # If line starts with '@attribute' and contains 'numeric',
                    # append intervening string as a column name,
                    # and store index as first line of column names:
                    if line.startswith('@attribute ') and 'numeric' in line:
                        if '{' in line:
                            interstring = line[11:line.index('{') - 1]
                        else:
                            interstring = line[11:line.index('numeric') - 1]

                        # If intervening string between '@attribute '
                        # and 'numeric' is not the exception_string,
                        # include as a column header:
                        if interstring != exception_string:
                            columns.append(interstring)
                            if not first_numeric:
                                first_numeric = True

                    # Else break if past first line
                    # that has '@attribute ' and 'numeric':
                    elif first_numeric:
                        break

            # Remove left and right (first and last) data items:
            data = lines[len(lines)-1].split(',')
            data = data[data_from_left:-data_from_right]

            if len(data) != len(columns):
                raise Warning("arff file doesn't conform to expected format.")

            # Construct a pandas Series:
            row_data = pd.Series(data, index=columns)

            # Save output_csv_file:
            if output_csv_file:
                row_data.to_csv(output_csv_file)

        except:
            row_data = None
            output_csv_file = None

    return row_data, output_csv_file


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
    >>> from mhealthx.xtra import concatenate_tables_vertically
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
            table_data = None
            output_csv_file = None

    return table_data, output_csv_file


def concatenate_tables_horizontally(tables, output_csv_file=None):
    """
    Horizontally concatenate multiple table files or pandas DataFrames
    that have the same number of rows and store as a csv table.

    If any one of the members of the tables list is itself a list,
    call concatenate_tables_vertically() on this list.

    Parameters
    ----------
    tables : list of strings or pandas DataFrames
        each component table has the same number of rows
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
    >>> from mhealthx.xtra import concatenate_tables_horizontally
    >>> df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
    >>>                     'B': ['B0', 'B1', 'B2', 'B3'],
    >>>                     'C': ['C0', 'C1', 'C2', 'C3']},
    >>>                    index=[0, 1, 2, 3])
    >>> df2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
    >>>                     'B': ['B4', 'B5', 'B6', 'B7'],
    >>>                     'C': ['C4', 'C5', 'C6', 'C7']},
    >>>                     index=[0, 1, 2, 3])
    >>> tables = [df1, df2]
    >>> output_csv_file = None #'./test.csv'
    >>> table_data, output_csv_file = concatenate_tables_horizontally(tables, output_csv_file)
    """
    import os
    import pandas as pd

    from mhealthx.xtra import concatenate_tables_vertically as cat_vert

    if tables is None:
        table_data = None
        output_csv_file = None
    else:
        try:
            # Create a list of pandas DataFrames:
            tables_to_combine = []
            for table in tables:
                # pandas DataFrame:
                if type(table) == pd.DataFrame:
                    tables_to_combine.append(table)
                # file string:
                elif type(table) == str:
                    if os.path.isfile(table):
                        table_from_file = pd.read_csv(table)
                        tables_to_combine.append(table_from_file)
                    else:
                        raise Warning('{0} is not a file.'.format(table))
                # list of tables to be vertically concatenated:
                elif type(table) == list:
                    out_file = None
                    subtable, out_file = cat_vert(table, out_file)
                    tables_to_combine.append(subtable)
                else:
                    raise Warning("'tables' members are not the right types.")
            tables = tables_to_combine

            # Raise an error if tables are not equal height pandas DataFrames:
            table0 = tables[0]
            nrows = table0.shape[0]
            for table in tables:
                if table.shape[0] != nrows:
                    raise Warning("The tables have different numbers"
                                  " of rows!")

            # Horizontally concatenate tables:
            table_data = pd.concat(tables, axis=1)

            # Store as csv file:
            if output_csv_file:
                table_data.to_csv(output_csv_file, index=False)
        except:
            table_data = None
            output_csv_file = None

    return table_data, output_csv_file


def concatenate_two_tables_horizontally(table1, table2, output_csv_file=None):
    """
    Horizontally concatenate two table files or pandas DataFrames
    that have the same number of rows and store as a csv table.

    If either of the tables is itself a list,
    concatenate_two_tables_horizontally() will call
    concatenate_tables_vertically() on this list.

    Parameters
    ----------
    table1 : string or pandas DataFrame
    table2 : string or pandas DataFrame
        same number of rows as table1
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
    >>> from mhealthx.xtra import concatenate_two_tables_horizontally
    >>> table1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
    >>>                     'B': ['B0', 'B1', 'B2', 'B3'],
    >>>                     'C': ['C0', 'C1', 'C2', 'C3']},
    >>>                    index=[0, 1, 2, 3])
    >>> table2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
    >>>                     'B': ['B4', 'B5', 'B6', 'B7'],
    >>>                     'C': ['C4', 'C5', 'C6', 'C7']},
    >>>                     index=[0, 1, 2, 3])
    >>> output_csv_file = None #'./test.csv'
    >>> table_data, output_csv_file = concatenate_two_tables_horizontally(table1, table2, output_csv_file)
    """
    from mhealthx.xtra import concatenate_tables_horizontally as cat_horz

    tables = [table1, table2]
    table_data, output_csv_file = cat_horz(tables, output_csv_file)

    return table_data, output_csv_file


# ============================================================================
# Run above functions to convert all voice files to wav and upload to Synapse:
# ============================================================================
if __name__ == '__main__':

    pass
