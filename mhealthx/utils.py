#!/usr/bin/env python
"""Utility functions.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def run_command(command, flag1='', arg1='', flags=[], args=[],
                flagN='', argN='', closing=''):
    """
    Run a generic command.

    Parameters
    ----------
    command : string
        name of command: "SMILExtract"
    flag1 : string
        optional first command line flag
    arg1 : string
        optional first argument, handy for iterating over in the pipeline
    flags : string or list of strings
        command line flags precede their respective args: ["-C", "-I", "-O"]
    args : string or list of strings
        command line arguments: ["config.conf", "input.wav", "output.csv"]
    flagN : string
        optional last command line flag
    argN : string
        optional last argument, handy for iterating over in the pipeline
    closing : string
        closing string in command

    Returns
    -------
    command_line : string
        full command line
    args : list of strings
        command line arguments
    arg1 : string
        optional first argument, handy for iterating over in the pipeline
    argN : string
        optional last argument, handy for iterating over in the pipeline

    Examples
    --------
    >>> from mhealthx.utils import run_command
    >>> command = 'ls'
    >>> flag1 = ''
    >>> arg1 = ''
    >>> flags = ['-l', '']
    >>> args = ['/software', '/desk']
    >>> flagN = ''
    >>> argN = ''
    >>> closing = '> test.txt'
    >>> command_line, args, arg1, argN = run_command(command, flag1, arg1, flags, args, flagN, argN, closing)

    """
    from nipype.interfaces.base import CommandLine

    try:
        # Join flags with args:
        if type(flags) == list and type(args) == list:
            flag_arg_tuples = zip(flags, args)
            flags_args = ''
            for flag_arg_tuple in flag_arg_tuples:
                flags_args = ' '.join([flags_args, ' '.join(flag_arg_tuple)])
        elif type(flags) == str and type(args) == str:
            flags_args = ' '.join([flags, args])
        else:
            raise IOError("-flags and -args should both be strings or lists")

        options = ' '.join([' '.join([flag1, arg1]), flags_args,
                            ' '.join([flagN, argN]), closing])
        command_line = ' '.join([command, options])

        # Nipype command line wrapper:
        cli = CommandLine(command=command)
        cli.inputs.args = options
        cli.cmdline
        cli.run()
    except:
        command_line = None
        args = None
        arg1 = None
        argN = None

    return command_line, args, arg1, argN


def rename_file(old_file, new_filename='', new_path='', file_append='',
                create_file=False):
    """Rename (and optionally copy) a file / path / file_append.

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
    new_file_name : string
        new file name (full path, if remove_path not set)

    Examples
    --------
    >>> from mhealthx.utils import rename_file
    >>> old_file = '/homedir/wav/test1.wav'
    >>> new_filename = ''
    >>> new_path = '.'
    >>> file_append = '.csv'
    >>> create_file = True
    >>> new_file_name = rename_file(old_file, new_filename, new_path, file_append, create_file)
    """
    import os
    from shutil import copyfile

    if old_file is None:
        new_file_name = None
    else:
        try:
            old_path, base_file_name = os.path.split(old_file)

            if new_filename:
                base_file_name = new_filename

            if new_path:
                new_file_name = os.path.join(new_path, base_file_name)
            else:
                new_file_name = os.path.join(old_path, base_file_name)

            if file_append:
                new_file_name = ''.join((new_file_name, file_append))

            if create_file:
                copyfile(old_file, new_file_name)
        except:
            new_file_name = None

    return new_file_name


