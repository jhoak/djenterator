import random
import music

# Default rates for random effect rolls (may be changed):
note_rate = 0.4
zero_rate = 0.75
mute_rate = 0.5
hammerpull_rate = 0.25
repeat_rate = 0.66
tremolo_rate = 0.66
mult_phrase_rate = 0.5

# Other globals
default_tuning = music.Tuning("drop", "a")
notes_per_phrase = 64
_bad_endings = ['h', 'p']

def _default_note_ls():
	return ['-'] * notes_per_phrase

def gen_phrase():
	lists = (_default_note_ls() for i in range(2))
	notes, mutes = lists
	random.seed()
	roll = random.random
	index = 0
	while index < notes_per_phrase:
		if roll() < note_rate:
			# Maybe add note and maybe a mute
			notes[index] = '0' if roll() < zero_rate else '1'
			if roll() < mute_rate:
				mutes[index] = 'm'
			index += 1

			# Now add effects
			adding = True
			while adding and index < notes_per_phrase - 1:
				if roll() < tremolo_rate:
					while index < notes_per_phrase - 1:
						if roll() < note_rate:
							notes[index] = '0' if roll() < zero_rate else '1'
							if roll() < mute_rate:
								mutes[index] = 'm'
							index += 1
						else:
							break
				if roll() < hammerpull_rate and index < notes_per_phrase - 1:
					notes[index:index + 2] = ['h', '1'] if notes[index - 1] == '0' else ['p', '0']
					if roll() < mute_rate:
						mutes[index + 1] = 'm'
					index += 2
				else:
					adding = False
		else:
			index += 1
	if roll() < repeat_rate:
		halfway = notes_per_phrase // 2
		notes[halfway:] = notes[0:halfway]
		mutes[halfway:] = mutes[:halfway]
		if notes[halfway-1] in _bad_endings:
			notes[halfway-1] = '-'
			notes[-1] = '-'
	return notes, mutes

def gen_song(min_phrases, tuning=default_tuning):
	num_phrases = 0
	song = music.Song(tuning)
	while num_phrases < min_phrases:
		# Generate a phrase and add to the song
		presets = gen_phrase()
		song.add_phrase(presets)
		num_phrases += 1

		# Duplicate it if we need to
		while random.random() < mult_phrase_rate:
			song.add_phrase(presets)
			num_phrases += 1
	return song