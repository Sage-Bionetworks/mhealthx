#!/usr/bin/env python
"""
Input/output functions to read and write data files or tables.

See synapse_io.py for reading from and writing to Synapse.org.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def convert_audio_file(old_file, file_append, new_file='', command='ffmpeg',
                       input_args='-i', output_args='-ac 2'):
    """
    Convert audio file to new format.

    Parameters
    ----------
    old_file : string
        full path to the input file
    file_append : string
        append to file name to indicate output file format (e.g., '.wav')
    new_file : string
        full path to the output file (optional)
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
    >>> from mhealthx.data_io import convert_audio_file
    >>> old_file = '/Users/arno/mhealthx_cache/mhealthx/feature_files/test.m4a'
    >>> file_append = '.wav'
    >>> new_file = 'test.m4a'
    >>> command = 'ffmpeg'
    >>> input_args = '-i'
    >>> output_args = '-ac 2'
    >>> converted_file = convert_audio_file(old_file, file_append, new_file, command, input_args, output_args)

    """
    import os
    from nipype.interfaces.base import CommandLine

    if old_file is None:
        converted_file = None
    else:
        if not os.path.isfile(old_file):
            converted_file = None
        else:
            try:
                ## Don't convert file if file already has correct append:
                #if old_file.endswith(file_append): converted_file=old_file

                # Convert file to new format:
                if new_file:
                    output_file = new_file + file_append
                else:
                    output_file = old_file + file_append

                # Don't convert file if output file already exists:
                #if os.path.isfile(output_file): converted_file=output_file

                # Nipype command line wrapper:
                cli = CommandLine(command = command)
                cli.inputs.args = ' '.join([input_args, old_file,
                                            output_args, output_file])
                cli.cmdline
                cli.run()
                converted_file = output_file
            except:
                converted_file = None

    return converted_file


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

    if arff_file is None:
        csv_file = None
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
            cols = []
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
                raise Warning("arff file doesn't conform to expected format.")

            # Write csv file:
            headers = ",".join(cols)
            data_string = ', '.join(data) + '\n'
            if not csv_file:
                csv_file = arff_file + '.csv'
            with open(csv_file, 'w') as fout:
                fout.write(headers)
                fout.write('\n')
                fout.writelines(data_string)
        except:
            csv_file = None

    return csv_file


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
    >>> from mhealthx.data_io import concatenate_tables_vertically
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
                pass
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
    Horizontally concatenate multiple table files or pandas DataFrames or
    dictionaries that have the same number of rows and store as a csv table.

    If any one of the members of the tables list is itself a list,
    call concatenate_tables_vertically() on this list.

    Parameters
    ----------
    tables : list of strings, pandas DataFrames, and/or lists of dicts
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
    >>> from mhealthx.data_io import concatenate_tables_horizontally
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

    from mhealthx.data_io import concatenate_tables_vertically as cat_vert

    if tables is None:
        table_data = None
        output_csv_file = None
    else:
#        try:
            # Create a list of pandas DataFrames:
            tables_to_combine = []
            for table in tables:
                # pandas DataFrame:
                if type(table) == pd.DataFrame:
                    tables_to_combine.append(table)
                # file string:
                elif type(table) == str:
                    if os.path.isfile(table):
                        table_from_file = pd.DataFrame.from_csv(table)
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
#        except:
#            table_data = None
#            output_csv_file = None

    return table_data, output_csv_file


def Nones_to_empty_csvs_in_list(csv_files):
    """
    Create an empty csv file of equal size as other inputs.

    Parameters
    ----------
    csv_files : list of strings
        each file should have the same number of rows, except for 'None'

    Returns
    -------
    output_csv_files : list of strings or None
        same as csv_files, except that Nones are replaced by empty csv files

    Examples
    --------
    >>> from mhealthx.data_io import Nones_to_empty_csvs_in_list
    >>> csv_files = ['/Users/arno/mhealthx_cache/mhealthx/retrieve_phonation_file/mapflow/_retrieve_phonation_file1/audio_audio.m4a-10349c95-7326-42de-a57f-08d228398d9d2367289341070419184.tmp.m4a.wav.csv.csv', '/Users/arno/mhealthx_cache/mhealthx/retrieve_phonation_file/mapflow/_retrieve_phonation_file1/audio_audio.m4a-10349c95-7326-42de-a57f-08d228398d9d2367289341070419184.tmp.m4a.wav.csv.csv']
    >>> output_csv_files = Nones_to_empty_csvs_in_list(csv_files)

    """
    import numpy as np
    import pandas as pd

    if csv_files is None:
        output_csv_files = None
    else:
        try:
            # Select an example csv file:
            example_csv = None
            for input in csv_files:
                if input is not None:
                    example_csv = input
                break

            # Create an empty csv file with the same dimensions and columns:
            if example_csv:
                df = pd.read_csv(example_csv)
                nan_row = np.empty(df.shape)
                nan_row.fill('nan')
                dfnew = pd.DataFrame(nan_row, columns=df.columns)
                empty_csv_file = 'empty_table.csv'
                dfnew.to_csv(empty_csv_file)

                # Loop through csv files, replacing None with the empty table:
                output_csv_files = []
                for csv in csv_files:
                    if csv is None:
                        output_csv_files.append(empty_csv_file)
                    else:
                        output_csv_files.append(csv)
            else:
                output_csv_files = None
        except:
            output_csv_files = None

        return output_csv_files


# ============================================================================
if __name__ == '__main__':

    pass