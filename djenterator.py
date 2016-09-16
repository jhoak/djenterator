"""
@palm mutes
@hammer-ons
@pull-offs
//slide up
//slide down
//vibrato
//bend
//harmonic
//pre bend
//bend release
//pre bend release
//bend release bend
//dead note

**also separate guitar(s)
"""
import random

notes = ['a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#']
notes_per_phrase = 16

def next_note(base_note, step):
	return notes[(notes.index(base_note) + step) % len(notes)]

class Tuning:
	def __init__(self, type='standard', base_note='e'):
		self.base_note = base_note
		self.increments = [5,5,4,5]
		type = type.lower()
		if type != 'standard' and type != 'drop':
			raise ValueError("Only standard or drop tuning, please.")
		self.increments.insert(0, (5 if type == 'standard' else 7))
	def notes(self):
		note_ls = [self.base_note]
		for i in range(5):
			note_ls.insert(len(note_ls), next_note(note_ls[i], self.increments[i]))
		return note_ls
	def __str__(self):
		return str(self.notes())

class PhraseLine:
	def __init__(self, base_note, num_notes):
		self.base_note = base_note
		self.notes = ['-'] * num_notes
	def __str__(self):
		start, end = self.base_note.rjust(2) + '|', '|'
		#mid = "".join(self.notes)
		qtr = notes_per_phrase // 4
		groups = self.notes[0:qtr], self.notes[qtr : 2*qtr], self.notes[2*qtr : 3*qtr], self.notes[3*qtr:]
		groups = ["".join(groups[i]) for i in range(4)]
		mid = "|".join(groups)
		return start + mid + end

class MuteLine:
	def __init__(self, num_notes):
		self.notes = ['-'] * num_notes
	def __str__(self):
		start, end = '  {', '}'
		#mid = "".join(self.notes)
		qtr = notes_per_phrase // 4
		groups = self.notes[0:qtr], self.notes[qtr : 2*qtr], self.notes[2*qtr : 3*qtr], self.notes[3*qtr:]
		groups = ["".join(groups[i]) for i in range(4)]
		mid = "|".join(groups)
		return start + mid + end

class Phrase:
	def __init__(self, tuning):
		num_notes = notes_per_phrase
		notes = tuning.notes()
		self.lines = [PhraseLine(notes[5-i], num_notes) for i in range(6)]
		self.mute_line = MuteLine(num_notes)
	def set_notes(self, preset_notes):
		self.lines[5].notes = preset_notes[0]
		self.mute_line.notes = preset_notes[1]
	def gen_notes(self, note_rate=0.5, zero_rate=0.75, mute_rate=0.5, hammerpull_rate=0.25):
		string_notes, mutes = self.lines[5].notes, self.mute_line.notes
		random.seed()
		roll = random.random
		i = 0
		while i < notes_per_phrase:
			if roll() < note_rate:
				# Maybe add note and maybe a mute
				string_notes[i] = '0' if roll() < zero_rate else '1'
				if roll() < mute_rate:
					mutes[i] = 'm'
				i += 1

				# Now add effects
				adding = True
				while adding and i < notes_per_phrase - 1:
					if roll() < hammerpull_rate:
						string_notes[i:i+2] = ['h', '1'] if string_notes[i-1] == '0' else ['p', '0']
						if roll() < mute_rate:
							mutes[i+1] = 'm'
						i += 2
					else:
						adding = False
			else:
				i += 1
		return string_notes, mutes
	def __str__(self):
		return '\n'.join([str(line) for line in (self.lines + [self.mute_line])])

class Song:
	def __init__(self, tuning, min_phrases, mult_phrase_rate = 0.7, note_rate=0.5):
		num_phrases = 0
		self.phrase_ls = []
		while num_phrases < min_phrases:
			# Generate a phrase OR copy an earlier one
			m = Phrase(tuning)
			

			notes, mutes = m.gen_notes(note_rate)
			

			self.phrase_ls.insert(num_phrases, m)
			num_phrases += 1
			# Duplicate it if we need to
			while random.random() < mult_phrase_rate:
				m = Phrase(tuning)
				m.set_notes((notes, mutes))
				self.phrase_ls.insert(num_phrases, m)
				num_phrases += 1
	def __str__(self):
		return '\n\n'.join([str(meas) for meas in self.phrase_ls])

if __name__ == '__main__':
	for i in range(25):
		t = Tuning('drop', 'a')
		s = Song(t, random.randint(80, 160), note_rate=0.42)
		f = open("songs/song" + str(i+1) + '.txt', 'w')
		f.write(str(s))
		f.close()