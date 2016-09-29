import random
import music

# Default rates for random effect rolls (may be changed):
note_rate = 0.5
zero_rate = 0.75
mute_rate = 0.5
hammerpull_rate = 0.2
measure_repeat_rate = 0.55
tremolo_rate = 0.4
phrase_repeat_rate = 0.5

# Other globals
default_tuning = music.Tuning("drop", "a")
notes_per_phrase = 64
_bad_endings = ['h', 'p']
_roll = random.random

def _default_note_ls():
	return ['-'] * notes_per_phrase

def _roll_note_and_mute():
	note = '0' if _roll() < zero_rate else '1'
	mute = 'm' if _roll() < mute_rate else '-'
	return note, mute

def _roll_tremolo(notes, mutes, index, end):
	while index < end - 1:
		if _roll() < note_rate:
			notes[index], mutes[index] = _roll_note_and_mute()
			index += 1
		else:
			break
	return index

def _add_hammerpull(notes, mutes, index):
	notes[index:index + 2] = ['h', '1'] if notes[index - 1] == '0' else ['p', '0']
	if _roll() < mute_rate:
		mutes[index + 1] = 'm'
	return index + 2

def _roll_effects(notes, mutes, start_index):
	adding = True
	index, end = start_index, len(notes)
	while adding and index < end - 1:
		tremolo = _roll() < tremolo_rate
		hammerpull = _roll() < hammerpull_rate
		if tremolo:
			index = _roll_tremolo(notes, mutes, index, end)
		if hammerpull and index < end - 1:
			index = _add_hammerpull(notes, mutes, index)
		if not tremolo and not hammerpull:
			adding = False
	return index

def _roll_repeated_measures(notes, mutes):
	if _roll() < measure_repeat_rate:
		halfway = len(notes) // 2
		notes[halfway:] = notes[:halfway]
		mutes[halfway:] = mutes[:halfway]
		if notes[halfway-1] in _bad_endings:
			notes[halfway-1] = '-'
			notes[-1] = '-'

def gen_phrase():
	lists = (_default_note_ls() for i in range(2))
	notes, mutes = lists
	index = 0
	while index < notes_per_phrase:
		if _roll() < note_rate:
			# Maybe add note and maybe a mute
			notes[index], mutes[index] = _roll_note_and_mute()
			index += 1

			# Maybe add other effects, too
			index = _roll_effects(notes, mutes, index)
		else:
			index += 1
	#_roll_repeated_measures(notes, mutes)
	return notes, mutes

def gen_song(min_phrases, max_phrases=None, tuning=default_tuning):
	num_phrases = 0
	song = music.Song(tuning)
	if not max_phrases:
		max_phrases = float("inf")
	while num_phrases < min(min_phrases, max_phrases):
		# Generate a phrase and add to the song
		presets = gen_phrase()
		song.add_phrase(presets)
		num_phrases += 1

		# Duplicate it if we need to
		while random.random() < phrase_repeat_rate and num_phrases < max_phrases:
			song.add_phrase(presets)
			num_phrases += 1
	return song
