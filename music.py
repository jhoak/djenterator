"""
This module contains abstractions of common musical constructs, to be used
in the process of djenteration.

Note that no octave information is included anywhere here. In a tuning, going
from the thickest string to the thinnest one, the note of the next string is
always assumed to be either the same octave or one octave higher than that of
the previous string. For example, if the thickest string is tuned to play D,
then in the standard tuning the next string will be G in the same octave. If
the first string were tuned to E, then the next one would be tuned to the A of
the next octave up.
"""

# Notes on the chromatic scale
CHROMATIC_NOTES = ('a', 'a#', 'b', 'c', 'c#', 'd',
                   'd#', 'e', 'f', 'f#', 'g', 'g#')

def next_note(base_note, offset):
    """
    Given a chromatic scale note, returns the one <offset> semitones up/down.

    The base note can be anything in CHROMATIC_NOTES, of course. offset must
    be an integer.
    """

    base_index = CHROMATIC_NOTES.index(base_note.lower())
    next_index = (base_index + offset) % len(CHROMATIC_NOTES)
    return CHROMATIC_NOTES[next_index]


class Tuning:
    """Abstraction for a guitar tuning for some given # of strings."""

    def __init__(self, tuning_type='standard', base_note='c#', num_strings=9):
        """
        Makes a new tuning for a guitar with some # of strings.

        Unless arguments are specified, each new tuning is aimed at a 9-string
        guitar and is in C# standard (so the notes are EBGDAEBF#C#), a not-so-
        uncommon djent tuning. (This assumes all 3 extra strings are thicker
        than the 6th string already.)

        tuning_type must be 'drop' or 'standard'. base_note can be anything in
        CHROMATIC_NOTES. num_strings must be an integer greater than 1.
        """

        self._base_note = base_note.lower()
        self._tuning_type = tuning_type.lower()

        # Add note for next-widest string (e.g. F# for above example tuning).
        # This varies based on the tuning type.
        self._notes = [base_note]
        next_offset = 7 if tuning_type == 'drop' else 5
        self._notes.append(next_note(base_note, next_offset))

        # Now determine notes of all other strings. Typically each string is
        # 5 semitones up from the last one (from thickest to thinnest) but
        # the second-to-last string is only 4 semis up from the third-to-last.
        second_to_last_str = num_strings - 2
        for i in range(2, num_strings):
            next_offset = 5 if i != second_to_last_str else 4
            base = self._notes[i - 1]
            self._notes.append(next_note(base, next_offset))

    def base_note(self):
        """Return the base note of this tuning (thickest string's note)."""
        return self._base_note

    def tuning_type(self):
        """Return this tuning's type (drop or standard)."""
        return self._tuning_type

    def notes(self):
        """Return the notes of this tuning in a tuple."""
        return tuple(self._notes)


def _get_qtr(i, ls):
    """
    Gets a given quarter of a list. 0=first quarter, 1=second, etc.

    i should be the ith quarter, where 0 <= i <= 3. ls should be the list, of
    course. The list must be of length at least 4.
    """

    qtr = len(ls) // 4
    start, end = i * qtr, (i + 1) * qtr
    return ls[start:end]


def _get_mid(line):
    """
    For a Phrase/MuteLine, return the representation of the notes.

    Typically this is like:
    010-|-10-|1110|0001

    This is a convenience function to help print phrase/mute lines. line
    must be either a PhraseLine or MuteLine object.
    """

    groups = tuple(_get_qtr(i, line.notes) for i in range(4))
    groups = ["".join(groups[i]) for i in range(4)]
    return "|".join(groups)


class _PhraseLine:
    """
    A line of notes on one string, used to build phrases.

    Notes are ordered by the time they are played, so the sequence 0111 means
    that a 0 is played, then three 1's are played. (In case you're wondering,
    a 0 is when you play an open string (don't hold any guitar frets) and a 1
    is when you hold the first fret of a string and strum it.)

    According to djent tradition, only the fattest string on the guitar will
    be played, and the guitarist may only play the open string or with the
    first fret held down.
    """

    def __init__(self, base_note, num_notes):
        """
        Form a PhraseLine given a string's note and the max # of notes.

        The '-' symbol conventionally means nothing is to be played at that
        time.

        base_note must be a note of the chromatic scale. num_notes must be
        a positive integer, at least 4.
        """

        self.base_note = base_note.lower()
        self.notes = ['-'] * num_notes


    def __str__(self):
        """
        Return the string representation of this line.

        These typically look something like:
        C#|0101|100-|0101|011-|
        which means the string is C#, and there are 14 notes played over
        four measures (which together define one phrase).
        """

        start, end = self.base_note.rjust(2) + '|', '|'
        mid = _get_mid(self)
        return start + mid + end


class _MuteLine:
    """
    Like PhraseLines, but specifies notes that will be played but muted.

    On a new tab this line will look like:
    C#|0101|100-|0101|011-|
      {--mm|m---|----|-m--}

    The 2nd line in the example represents the actual MuteLine and says that
    the above note will be muted. (The 1st line of course is just a Phrase
    Line.)
    """
    def __init__(self, num_notes):
        """
        Given the max # of notes for this phrase, make a MuteLine.

        Like PhraseLines, '-' means don't mute the note above it.

        num_notes must be an integer, at least 4.
        """
        self.notes = ['-'] * num_notes


    def __str__(self):
        """Returns the string representation of this line, described above."""

        start, end = '  {', '}'
        mid = _get_mid(self)
        return start + mid + end


class _Phrase:
    """A musical phrase, represented here by a set of four measures."""

    def __init__(self, tuning, num_notes, num_strings):
        """
        Make a new phrase, given a tuning, max # of notes, and # of strings.

        tuning must be a Tuning object, num_notes must be an integer >= 4, and
        num_strings must be an integer >= 2.
        """

        tuning_notes = tuning.notes()
        strs = num_strings
        self.num_strings = strs

        def make_phrase_line(string_num):
            """
            Makes a PhraseLine given a base note and # of notes in a phrase.
            """
            base_note = tuning_notes[strs - string_num - 1]
            return _PhraseLine(base_note, num_notes)

        # Initialize each line in the phrase (1 for each guitar string)
        self.lines = [make_phrase_line(i) for i in range(strs)]
        self.mute_line = _MuteLine(num_notes)


    def set_notes(self, notes, mutes):
        """
        Set the notes + mutes for this phrase, given them as arguments.

        notes and mutes must be lists of equal length. notes must only have
        notes of the chromatic scale or -'s, and mutes must have only -'s or
        m's.
        """
        last_string = self.lines[self.num_strings-1]
        last_string.notes = notes
        self.mute_line.notes = mutes


    def __str__(self):
        """
        Returns the string representation of this phrase.

        Generally, phrases look like:
         E|----|----|----|----|
         B|----|----|----|----|
         G|----|----|----|----|
         D|----|----|----|----|
         A|----|----|----|----|
         E|0101|100-|0101|011-|
          {--mm|m---|----|-m--}

        Again, due to ancient djent tradition, no strings other than the
        widest one are to be played, which explains why notes are only on
        the lower E string here.
        """
        lines = [str(line) for line in self.lines + [self.mute_line]]
        return '\n'.join(lines)


class Song:
    """
    Represents a series of phrases, in the simplest sense.

    Each song initially has no phrases, but add_phrase() calls are used
    to build it up.
    """

    def __init__(self, tuning):
        """
        Makes an empty song given a guitar tuning to use.

        tuning must be an instance of the Tuning class.
        """

        self._phrase_ls = []
        self._tuning = tuning


    def tuning(self):
        """Returns this song's tuning."""

        return self._tuning


    def add_phrase(self, notes, mutes):
        """
        Adds a phrase to this, given a set of notes and mutes to use.

        notes and mutes must be lists of equal length. notes must only have
        notes of the chromatic scale or -'s, and mutes must have only -'s or
        m's.
        """

        num_notes = len(notes)
        num_strings = len(self._tuning.notes())

        phrase = _Phrase(self._tuning, num_notes, num_strings)
        phrase.set_notes(notes, mutes)
        self._phrase_ls.append(phrase)


    def __str__(self):
        """
        Returns the string representation of this song.

        Each song is, as stated, a series of phrases. It is simply represented
        as all of the phrases with two newlines between each pair.
        """

        return '\n\n'.join([str(p) for p in self._phrase_ls])
