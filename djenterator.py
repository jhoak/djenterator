"""\
Here's a docstring!
"""

import random, re
from os import path, makedirs
from sys import argv, platform, exit, maxsize as maxint
from djentils import gen_song

# Globals
_on_windows = re.match(platform, 'win') or re.match(platform, 'cygwin')
path_sep = '\\' if _on_windows else '/'

# Generator options (changed by args)
_names = ('numfiles', 'filename', 'dirname', 'minphrases', 'maxphrases', 'force_overwrites')
_default_vals = (1, 'i_love_djent.txt', './djenterated_songs', random.randint(80,120), maxint, False)
_defaults = dict(zip(_names, _default_vals))
options = _defaults.copy()

def trim_quotes(string):
	quotes = ("'", '"')
	while string[0] in quotes and string[-1] in quotes:
		string = string[1:-1]
	return string

def getkey(keystr):
	option_names = ('-n', '-o', '-d', '-min', '-max', '-f')
	option_map = dict(zip(option_names, _names))
	if keystr in option_map.keys():
		return option_map[keystr]
	else:
		raise ValueError('Invalid argument', keystr)

def toint(string):
	try:
		num = int(string)
		if num < 1:
			raise ValueError()
		return num
	except ValueError:
		raise ValueError("Invalid numerical parm " + string)

def whole_filename(dirname, filename):
	last = dirname[-1]
	if last != path_sep:
		dirname += path_sep
	return dirname + filename

def add_filenum(name, num):
	if '.' not in name:
		return name + str(num)
	else:
		index = name.rfind('.')
		return name[:index] + str(num) + name[index:]

def get_bool_resp(prompt):
	while True:
		resp = input(prompt).lower()
		if resp in ('y', 'yes'):
			return True
		elif resp in ('n', 'no'):
			return False

def process_other_input(args):
	global options
	index = 0
	while index < len(args):
		try:
			arg = trim_quotes(args[index])
			key = getkey(arg)
			if key == 'force_overwrites':
				options[key] = True
				index += 1
			else:
				value = trim_quotes(args[index+1])
				if type(options[key]) is int:
					value = toint(value)
				options[key] = value
				index += 2
		except ValueError as err:
			return err
	return None

def djenterate():
	numfiles, filename, dirname = (options[name] for name in _names[:3])
	minphrases, maxphrases, force_overwrites = (options[name] for name in _names[3:])
	if not path.isdir(dirname):
		makedirs(dirname)
	for i in range(numfiles):
		song = gen_song(minphrases, maxphrases)
		songfile = whole_filename(dirname, filename)
		if numfiles > 1:
			songfile = add_filenum(songfile, i + 1)
		if path.isfile(songfile):
			prompt = "Overwrite file \"" + songfile + "\"? (Y/N): "
			overwrite = force_overwrites or get_bool_resp(prompt)
			if not overwrite:
				continue
		f = open(songfile, 'w')
		f.write(str(song))
		f.close()
	return 0

if __name__ == '__main__':
	args = argv[1:]
	if '-help' in args:
		print(__doc__)
		exit(0)

	err = process_other_input(args)
	if err:
		print("ERROR:", err)
		exit(-1)
	else:
		exit(djenterate())