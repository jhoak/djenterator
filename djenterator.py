import random, os
import djentils

if __name__ == '__main__':
	if not os.path.isdir("./songs"):
		os.mkdir("songs")
	for i in range(25):
		min_phrases = random.randint(80,160)
		song = djentils.gen_song(min_phrases)
		songfile = "songs/song" + str(i + 1) + ".txt"
		f = open(songfile, 'w')
		f.write(str(song))
		f.close()