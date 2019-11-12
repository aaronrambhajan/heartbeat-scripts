import librosa
import os

"""
Prototype script for detecting transients.
"""

filename = ''
# Filenames
regular = [f for f in os.listdir("../sounds/regular") if os.path.isfile(os.path.join("../sounds/regular/", f)) and ('wav' in f)]

filename = "../sounds/regular/" + regular[0]
y, sr = librosa.load(filename)

tempo = librosa.beat.tempo(y=y, sr=sr, aggregate=None)

print(tempo)

onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units = 'time')
librosa.frames_to_time(onset_frames, sr=sr)

print(onset_frames)


