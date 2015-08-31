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
    >>> command_line, args = run_command(command, flag1, arg1, flags, args, flagN, argN, closing)

    """
    from nipype.interfaces.base import CommandLine

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

    # Return args:
    return command_line, args, arg1, argN


def change_filenames(file_names, new_path='', remove_path=False, suffix=''):
    """Change path, name, and add a suffix to files.

    Parameters
    ----------
    file_names : list of strings
        file names (full path)
    new_path : string
        replacement path
    remove_path : Boolean
        remove path?
    suffix : string
        append to file names

    Returns
    -------
    new_file_names : list of strings
        new file names (full path, if remove_path not set)

    Examples
    --------
    >>> from mhealthx.utils import change_filenames
    >>> file_names = ['/home/arno/wav/test1.wav', '/home/arno/wav/test2.wav']
    >>> new_path = '/home/arno'
    >>> remove_path = False
    >>> suffix = '.csv'
    >>> new_file_names = change_filenames(file_names, new_path, remove_path, suffix)
    """
    import os

    new_file_names = []
    for i, file_name in enumerate(file_names):

        if remove_path or new_path:
           base_file_name = os.path.basename(file_name)

        if remove_path:
            file_name = base_file_name

        if new_path:
            file_name = os.path.join(new_path, base_file_name)

        if suffix:
            file_name = ''.join((file_name, suffix))

        new_file_names.append(file_name)

    return new_file_names


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
    >>> from mhealthx.synapse_io import convert_audio_files
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


