import random, re
from os import path, makedirs
from sys import argv, platform, exit
from djentils import gen_song

# Globals
_on_windows = re.match(platform, 'win') or re.match(platform, 'cygwin')
# Default options (changed by args)
path_sep = r'\' if _on_windows else '/'
force_overwrites = False
num_files = 1
file_name = 'i_love_djent.txt'
dir_name = '.'
min_phrases = randint(80, 120)
max_phrases = None

def whole_filename():
	global dir_name
	last = dir_name[-1]
	if last != path_sep:
		dir_name += path_sep
	return dir_name + file_name

def add_filenum(name, num):
	if '.' not in name:
		return name + str(num)
	else:
		index = name.rfind('.')
		return name[:index] + str(num) + name[index:]

def get_bool_resp(prompt):
	while True:
		resp = input(prompt).to_lower()
		if resp in ('y', 'yes'):
			return True
		elif resp in ('n', 'no'):
			return False

def process_args(args):
	

def djenterate():
	if not path.isdir(dir_name):
		makedirs(dir_name)
	for i in range(num_files):
		song = gen_song(min_phrases, max_phrases)
		songfile = whole_filename()
		if num_files > 1:
			songfile = add_filenum(songfile, i + 1)
		if path.isfile(songfile):
			overwrite = force_overwrites or get_bool_resp(prompt)
			if not overwrite:
				continue
		f = open(songfile, 'w')
		f.write(str(song))
		f.close()
	return 0

if __name__ == '__main__':
	sys.exit(djenterate())
