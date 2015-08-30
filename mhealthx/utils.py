#!/usr/bin/env python
"""Utility functions.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def run_command(command, flags=[], args=[], closing=''):
    """
    Run a generic command.

    Parameters
    ----------
    command : string
        name of command: "SMILExtract"
    flags : string or list of strings
        command line flags precede their respective args: ["-C", "-I", "-O"]
    args : string or list of strings
        command line arguments: ["config.conf", "input.wav", "output.csv"]
    closing : string
        closing string in command

    Returns
    -------
    command_line : string
        full command line
    args : list of strings
        command line arguments

    Examples
    --------
    >>> from mhealthx.utils import run_command
    >>> command = 'ls'
    >>> flags = ['-l', '']
    >>> args = ['/software', '/desk']
    >>> closing = '> test.txt'
    >>> command_line, args = run_command(command, flags, args, closing)

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

    options = ' '.join([flags_args, closing])
    command_line = ' '.join([command, options])

    # Nipype command line wrapper:
    cli = CommandLine(command=command)
    cli.inputs.args = options
    cli.cmdline
    cli.run()

    # Return args:
    return command_line, args


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


