"""
This module contains the main script used to generate new songs.
It will NOT send songs to stdout but rather write them to files
on disk, based on the passed parameters (if any).

Usage: python djenterator.py [-help] [-n <number>] [-o <filename>]
        [-d <directoryname>] [-min <number>] [-max <number>] [-f]
Parameters:
    -help   Show this helpful info.
    -n      Specifies the number of files to generate, aka the number of songs
    -o      The name of the output file.
    -d      The directory where the output file should be placed.
    -min    The minimum number of phrases to generate in each song. (Note that
            the resulting number of phrases will still be a bit random.)
    -max    The maximum number of phrases to generate in each song.
    -f      Forcibly overwrite files when generated song files have the same
            name as files in the output directory.
"""

import random
import re
from os import path, makedirs
from sys import argv, platform, exit as sysexit, maxsize as maxint
from djenterator.djentils import gen_song

# Globals for convenience
_ON_WINDOWS = re.match(platform, 'win') or re.match(platform, 'cygwin')
_PATH_SEP = '\\' if _ON_WINDOWS else '/'
_QUOTES = ('\'', "\"")

# Make list of possible parms and map to a set of default values
_SHORT_PARM_NAMES = ('-n', '-o', '-d', '-min', '-max', '-f')
_FULL_PARM_NAMES = ('numfiles', 'filename', 'dirname',
                    'minphrases', 'maxphrases', 'force_overwrites')
_PARM_MAP = dict(zip(_SHORT_PARM_NAMES, _FULL_PARM_NAMES))

_DEFAULT_PARM_VALS = (1, 'i_love_djent.txt', './djenterated_songs',
                      random.randint(80, 120), maxint, False)
_DEFAULTS_MAP = dict(zip(_FULL_PARM_NAMES, _DEFAULT_PARM_VALS))
OPTIONS = _DEFAULTS_MAP.copy()


# Convenience Methods
def _trim_quotes(string):
    """Takes a string with surrounding quotes and removes the quotes."""

    while string[0] in _QUOTES and string[-1] in _QUOTES:
        string = string[1:-1]
    return string


def _getkey(keystr):
    """
    Returns the full parm-name corresponding to a short one.
    Example: -d -> dirname

    keystr must be in _SHORT_PARM_NAMES.
    """

    if keystr in _PARM_MAP.keys():
        return _PARM_MAP[keystr]
    else:
        raise ValueError('Invalid argument', keystr)


def _to_pos_int(string):
    """Gets a positive int from a string and returns it."""

    try:
        num = int(string)
        if num < 1:
            raise ValueError()
        return num
    except ValueError:
        raise ValueError("Invalid numerical parm " + string)


def _whole_filename(dirname, filename):
    """
    Puts together a filename including the file itself plus the directory.

    Example: C/Users/Edgar/Desktop/secret.txt

    dirname must be a directory name. filename must be a file name (for this,
    no files nested in directories, please; an example would be foo/bar.txt)
    """

    last = dirname[-1]
    if last != _PATH_SEP:
        dirname += _PATH_SEP
    return dirname + filename


def _add_filenum(name, num):
    """
    Adds a number to a file (when we're generating >1 file)
    Example: i_love_djent.txt -> i_love_djent1.txt, i_love_djent2.txt, ...

    name should be a filename, which may or may not have an extension. num
    should be a real number >= 0.
    """

    if '.' not in name:
        return name + str(num)
    else:
        index = name.rfind('.')
        return name[:index] + str(num) + name[index:]


def _get_bool_resp(prompt):
    """
    Gets a yes or no from user input and maps to a boolean.

    prompt should be a String that contains a user prompt (e.g., "Please input
    your name: ")
    """

    while True:
        resp = input(prompt).lower()
        if resp in ('y', 'yes'):
            return True
        elif resp in ('n', 'no'):
            return False


def _process_other_input(arg_ls):
    """Processes a list of command-line args (but not -help)."""

    index = 0
    while index < len(arg_ls):
        try:
            # Get the associated parm name
            arg = _trim_quotes(arg_ls[index])
            key = _getkey(arg)
            if key == 'force_overwrites':
                OPTIONS[key] = True
                index += 1
            else:
                # Handle parms of the form -name <value>
                value = _trim_quotes(arg_ls[index+1])

                # If it's a string but the parm type should be int, convert it
                if isinstance(OPTIONS[key], int):
                    value = _to_pos_int(value)
                OPTIONS[key] = value
                index += 2
        except ValueError as err:
            # Bad argument somehow
            return err
    return None


def _writefile(filename, song):
    """
    Opens a file and writes a song tab to it.

    filename is the name of the file to open. song must be a Song object.
    """

    songfile = open(filename, 'w')
    songfile.write(str(song))
    songfile.close()


def djenterate():
    """
    Based on the OPTIONS we got (after processing args), make a song(s).

    Calling this method without doing any input processing will just
    generate a song using default settings. process_other_args() should be
    called first. And before that, also need to check if -help was specified.
    """

    # Get our OPTIONS and their values
    value_of = lambda name: OPTIONS[name]
    option_vals = list(map(value_of, _FULL_PARM_NAMES))
    numfiles, filename, dirname = option_vals[:3]
    minphrases, maxphrases, force_overwrites = option_vals[3:]

    # Make the directory(ies) if it doesn't exist yet
    if not path.isdir(dirname):
        makedirs(dirname)

    # Generate <numfiles> songs
    for i in range(numfiles):
        song = gen_song(minphrases, maxphrases)
        songfile = _whole_filename(dirname, filename)

        # Number files to avoid conflicts if we have more than 1
        if numfiles > 1:
            songfile = _add_filenum(songfile, i + 1)

        # Also make sure not to overwrite if not forcing and user says not to
        if path.isfile(songfile):
            prompt = "Overwrite file \"" + songfile + "\"? (Y/N): "
            overwrite = force_overwrites or _get_bool_resp(prompt)
            if not overwrite:
                continue
        _writefile(songfile, song)
    return 0


# Main script layout. Process args then djenterate some songs
if __name__ == '__main__':
    args = argv[1:]

    # Check if -help is specified here, just for convenience
    if '-help' in args:
        print(__doc__)
        sysexit(0)

    err = _process_other_input(args)
    if err:
        print("ERROR:", err)
        sysexit(-1)
    else:
        sysexit(djenterate())
