"""
This module provides abstractions for musical structures, i.e.
the chromatic scale, phrases, guitar tunings, and entire songs (many phrases).
"""

# Globals: Chromatic scale notes and possible tuning types
chromatic_notes = ('a', 'a#', 'b', 'c', 'c#', 'd', 
				   'd#', 'e', 'f', 'f#', 'g', 'g#')
tuning_types = ('drop', 'standard')

def next_note(base_note, offset):
	"""
	Given a note on the chromatic scale, returns the next note with given
	offset from it.
	"""
	this_index = chromatic_notes.index(base_note)
	next_index = (this_index + offset) % len(chromatic_notes)
	return chromatic_notes[next_index]

class Tuning:
	"""
	Represents a guitar tuning for any guitar with 4+ strings. Given a base
	note and tuning type (drop or standard) as well as a number of strings,
	this will generate the notes of the corresponding tuning. (i.e. E standard
	becomes EADGBE for a 6-string)
	"""

	def __init__(self, type='standard', base_note='c#', num_strings=9):
		"""
		Generates a tuning given a type, base note, and number of strings on a
		guitar.

		The possible types are "drop" or "standard". Base notes can be anything
		on the chromatic scale. The number of strings must be at least 4.
		"""

		# Tuning is represented as a series of notes starting at a base note
		self.base_note = base_note
		self.increments = ([5] * (num_strings - 4)) + [4,5]

		# Add first increment based on tuning type (drop -> 2 semitones lower)
		self.increments.insert(0, (7 if type == 'drop' else 5))

	def notes(self):
		"""
		Generates and returns the notes of the tuning from the base note and
		increments.
		"""
		note_ls = [self.base_note]
		for i in range(len(self.increments)):
			note_ls.insert(len(note_ls), next_note(note_ls[i], self.increments[i]))
		return tuple(note_ls)


class PhraseLine:
	"""
	Represents the notes on a particular string that are to be played in one
	phrase. Because this is the djenterator, all but 1 string will be silent
	during every single song.
	"""
	def __init__(self, base_note, num_notes):
		"""
		Initialized using the string's base note and the number of notes
		that will be played in this phrase (4 measures).
		"""

		self.base_note = base_note
		self.notes = ['-'] * num_notes

	def __str__(self):
		"""
		Returns the string representation of this line of notes.

		Generally, it appears as a note followed by a set of four measures
		(sets of 0s, 1s, and -'s, generally) separated by vertical lines, like:
		A#|--01|010-|0111|10-1|

		Of course, this represents the notes on just one string.
		"""
		start, end = self.base_note.rjust(2) + '|', '|'
		qtr = len(self.notes) // 4

		# Generate each of the four measures, then compose each one by their
		# notes individually then concatenate with vertical bars inbetween
		groups = tuple(self.notes[i * qtr:(i+1) * qtr] for i in range(4))
		groups = ["".join(groups[i]) for i in range(4)]
		mid = "|".join(groups)
		return start + mid + end


class MuteLine:
	"""Same as a phrase line, but this indicates which notes will be muted."""

	def __init__(self, num_notes):
		"""Creates a mute line. Only checks that the number of notes is OK."""
		self.notes = ['-'] * num_notes

	def __str__(self):
		"""Makes a String representation of the line.

		The resulting representation will look like the 2nd line in the
		following example:

		C#|--01|010-|0111|10-1|
		  {--mm|m-m-|--mm|mm--}

		Here, 'm' says a note should be muted, but the '-' indicates that
		a note should not be.
		"""

		start, end = '  {', '}'
		qtr = len(self.notes) // 4
		
		# Generate each of the four measures, then compose each one by their
		# notes individually then concatenate with vertical bars inbetween
		groups = tuple(self.notes[i * qtr:(i+1) * qtr] for i in range(4))
		groups = ["".join(groups[i]) for i in range(4)]
		mid = "|".join(groups)
		return start + mid + end


class Phrase:
	"""
	Represents a musical phrase; in this simple case, this is assumed to be
	just 4 measures. 

	(Note: Measures are not explicitly defined; when we generate
	notes, we generate them for the whole phrase, and they are separated
	into measures afterwards.)
	"""

	def __init__(self, tuning, num_notes, num_strings):
		"""
		Creates and initializes a new phrase given a specific tuning and
		number of notes and strings to use.
		"""

		notes = tuning.notes()
		strs = num_strings
		self.num_strings = strs
		self.lines = [PhraseLine(notes[strs-i-1], num_notes) for i in range(strs)]
		self.mute_line = MuteLine(num_notes)

	def set_notes(self, preset_notes):
		"""
		Sets the notes of this phrase according to a given preset, including
		both notes and mutes.

		The presets must contain exactly two elements. The first is the line of
		notes corresponding to the notes to be played on the last string. The
		second is the sequence of mutes associated with the given notes. Of
		course, these must be of the same length.
		"""

		last_string = self.lines[self.num_strings-1]
		last_string.notes = preset_notes[0]
		self.mute_line.notes = preset_notes[1]

	def __str__(self):
		"""Returns this as a string, e.g. phrase + mute lines joined by newlines."""
		lines = [str(line) for line in (self.lines + [self.mute_line])]
		return '\n'.join(lines)

class Song:
	"""
	Represents a collection of phrases, which are in turn a collection of lines
	on each string (over multiple measures), which are a collection of a
	specified number of notes.
	"""

	def __init__(self, tuning):
		"""Creates a new Song, though phrases must be added manually."""
		self.phrase_ls = []
		self.tuning = tuning

	def add_phrase(self, presets):
		p = Phrase(self.tuning, len(presets[0]), len(self.tuning.notes()))
		p.set_notes(presets)
		end_index = len(self.phrase_ls)
		self.phrase_ls.insert(end_index, p)

	def __str__(self):
		return '\n\n'.join([str(meas) for meas in self.phrase_ls])