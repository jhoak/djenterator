"""
This module holds functions that are used by the djenterator module by default
to djenterate new songs. The functions rely on various probabilities defined
in this file to generate random tabs; these probabilities are public and can
be adjusted to your liking. The number of notes in a phrase can be adjusted,
too.
"""

import random
import djenterator.music as music

# Options (can be adjusted)
NOTES_PER_PHRASE = 64       # Or 4x the number of notes per measure.

# Probability Name          # Frequency of...
NOTE_RATE = 0.5             # ...normal notes
ZERO_RATE = 0.75            # ...open-string notes (as opposed to 1st-frets)
MUTE_RATE = 0.5             # ...palm-muted notes
HAMMERPULL_RATE = 0.2       # ...hammer-ons/pull-offs
MEASURE_REPEAT_RATE = 0.55  # ...repeating first 1/2 of phrase in second 1/2
TREMOLO_RATE = 0.4          # ...tremolo-picking
PHRASE_REPEAT_RATE = 0.5    # ...repeating an entire phrase in next phrase

# Other globals
_DEFAULT_TUNING = music.Tuning("drop", "a")
_roll = random.random
_BAD_ENDINGS = ['h', 'p']   # Phrases cannot end in these


def _empty_note_ls():
    """Returns an "empty line" (see music.py)."""
    return ['-'] * NOTES_PER_PHRASE


def _roll_note_and_mute():
    """Picks the next note (0 or 1) and may/may not mute it."""

    note = '0' if _roll() < ZERO_RATE else '1'
    mute = 'm' if _roll() < MUTE_RATE else '-'
    return note, mute


def _roll_tremolo(notes, mutes, index, end):
    """
    Adds notes to a tremolo section; might add none by chance.

    notes and mutes must be lists of equal length. notes must only have
    notes of the chromatic scale (or -'s), and mutes must have only -'s or
    m's. index must be an integer > 0 but less than the length of either list.
    end must be the last index (exclusive!).
    """

    while index < end - 1:
        if _roll() < NOTE_RATE:
            notes[index], mutes[index] = _roll_note_and_mute()
            index += 1
        else:
            break
    return index


def _add_hammerpull(notes, mutes, index):
    """
    Adds a hammer-on/pull off depending on last note.

    The resulting note might be muted. Also the first note might be muted.
    So you can hammer-on a muted open string into a nonmuted 1st-fret.
    ...Why? Well, why not?

    As before: notes and mutes must be lists of equal length. notes must only
    have notes of the chromatic scale (or -'s), and mutes must have only -'s
    or m's. index must be an integer > 0 but less than the length of either
    list.
    """

    toadd = ['h', '1'] if notes[index - 1] == '0' else ['p', '0']
    notes[index:index + 2] = toadd
    if _roll() < MUTE_RATE:
        mutes[index + 1] = 'm'
    return index + 2


def _roll_effects(notes, mutes, start_index):
    """
    Uses probability to add tremolo or hammer-on/pulloff after the last note.

    As before: notes and mutes must be lists of equal length. notes must only
    have notes of the chromatic scale (or -'s), and mutes must have only -'s
    or m's. start_index must be an integer > 0 but less than the length of
    either list.
    """

    adding = True
    index, end = start_index, len(notes)
    while adding and index < end - 1:
        # According to chance, maybe add tremolo and maybe add HO/POs.
        tremolo = _roll() < TREMOLO_RATE
        hammerpull = _roll() < HAMMERPULL_RATE
        if tremolo:
            index = _roll_tremolo(notes, mutes, index, end)
        if hammerpull and index < end - 1:
            index = _add_hammerpull(notes, mutes, index)

        # If nothing was added this iteration, stop adding effects
        if not tremolo and not hammerpull:
            adding = False
    return index


def _roll_repeated_measures(notes, mutes):
    """
    Repeat the 1st 1/2 of a phrase in the 2nd 1/2 (according to chance.

    notes and mutes must be lists of equal length. notes must only have notes
    of the chromatic scale (or -'s), and mutes must have only -'s or m's.
    """

    if _roll() < MEASURE_REPEAT_RATE:
        halfway = len(notes) // 2
        notes[halfway:] = notes[:halfway]
        mutes[halfway:] = mutes[:halfway]

        # If we end on an invalid hammer-on/pull off 'h' or 'p', reroll a note
        if notes[halfway-1] in _BAD_ENDINGS:
            notes[halfway-1], mutes[halfway-1] = _roll_note_and_mute()


def _gen_phrase():
    """Generates a phrase of a song."""

    notes = _empty_note_ls()
    mutes = _empty_note_ls()
    index = 0
    while index < NOTES_PER_PHRASE:
        # Add a note (by probability). If successful, add effects
        if _roll() < NOTE_RATE:
            notes[index], mutes[index] = _roll_note_and_mute()
            index += 1

            index = _roll_effects(notes, mutes, index)
        # If unsuccessful, just move to the next note position in the tab
        else:
            index += 1
    return notes, mutes


def gen_song(min_phrases, max_phrases=None, tuning=_DEFAULT_TUNING):
    """
    Generates a new song (series of phrases) and returns it.

    Song length here is just measured by the number of phrases (no time or
    tempo involved). Probabilities used by this generator are, as stated,
    described above.

    min_phrases and max_phrases must be integer >= 0 (though max_phrases can
    be None, or omitted). tuning must be a Tuning object, but by default,
    drop A on a 9-string guitar will be used.
    """

    num_phrases = 0
    song = music.Song(tuning)
    if not max_phrases:
        max_phrases = float("inf")

    # Generally, djenterate at least min_phrases but no more than max
    while num_phrases < min(min_phrases, max_phrases):
        notes, mutes = _gen_phrase()
        song.add_phrase(notes, mutes)
        num_phrases += 1

        # By chance, we can also repeat a phrase more than once
        while random.random() < PHRASE_REPEAT_RATE and num_phrases < max_phrases:
            song.add_phrase(notes, mutes)
            num_phrases += 1
    return song
