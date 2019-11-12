"""
Suite of functions for the synthesis of heartbeats. Adapted and inspired
by [Ben C. Holmes'](https://github.com/bencholmes/heartbeat) MATLAB script.
"""

import numpy as np
from numpy import array as npArray
from numpy import arange, zeros, ones, absolute, array, float32
from numpy.random import uniform as rand
from scipy.signal import butter, iirpeak, hanning, lfilter
from scipy.io.wavfile import write as audiowrite
from math import ceil, floor
from matplotlib import pyplot as plt
from librosa import display, stft, power_to_db, load, output
from pysndfx import AudioEffectsChain
from os import remove


def processEffects(files):
	"""
	"""
    rec = ['../media/set2/S3_1final.wav', '../media/set2/S3_2final.wav', \
		'../media/set2/S3_3final.wav', '../media/set2/S3_4final.wav', \
		'../media/set2/S3_5final.wav', '../media/set2/S3_6final.wav', \
		'../media/set2/S3_7final.wav', '../media/set2/S3_8final.wav', \
			'../media/set2/S3_9final.wav', '../media/set2/S3_10final.wav']

    fx = (
        AudioEffectsChain()
        .reverb(reverberance=5, hf_damping=15, room_scale=20, stereo_depth=30)
        .pitch(shift=300)
        )

    for x in rec:
        infile = x
        outfile = x.replace('final', 'v5')
        fx(infile, outfile)


def makeHeartbeats(
	filename="python_heartbeat", numBeats=10, tempoBpm=100, 
	fs=44100, includeThird=0, write=False
):
	"""
	Creates numBeats heartbeats cycles, outputting as WAV.

	@filename str
		Name of the file
	@numBeats int   
		The number of beats in the recording
	@tempoBpm int   
		The tempo of the heartbeat
	@fs int   
		Sample rate
	@includeThird int
		Specifies the volume of S3. Defaults to 0 (meaning no S3), otherwise, 
		takes a value between 1 and 10 where 5* is the default.

	@returns None
		Outputs a WAV to the filename.
	"""
	# Calculate the duration of one beat and all the beats.
	beatDur = (60/tempoBpm) # 100 / MINUTE
	totalDur = beatDur*numBeats # duration of a single beat, multiplied over the number of beats

	# Number of samples for respective durations
	beatNs = floor(beatDur*fs)
	totalNs = floor(totalDur*fs)

	# Vectors for plotting against
	timeVec = [ (var/fs) for var in range(totalNs)]
	frequencyVec = [ (var * (fs/totalNs)) for var in range(totalNs)]

	# Structure
	hbConcatenated, hbConcatenatedUnfiltered = [], []

	# Simulate
	for nn in range(1, numBeats+1):
		[tempFilteredHb, tempUnfilteredHb] = singleHeartbeat(fs, beatDur, \ 
			tempoBpm, pulseThree=includeThird)
		hbConcatenated = _concatArrays([hbConcatenated, tempFilteredHb])
		hbConcatenatedUnfiltered = _concatArrays([hbConcatenatedUnfiltered, \
			tempUnfilteredHb])

	# Normalize
	# maxAbs = max(np.abs(hbConcatenated))
	# y = array([(num / maxAbs) for num in hbConcatenated], dtype=float32)

	# if checkDB:
	# return dbFromVol(hbConcatenated, tempoBpm=tempoBpm, fs=fs, graph=True)

	# Export
	if write:
		audiowrite('../media/{}.wav'.format(filename), fs, hbConcatenated)


def singleHeartbeat(fs, beatDur, tempo, pulseThree):
	"""
	Creates a single heartBEAT. A heartbeat is one full cycle of a beat, as
	illustrated by a Wiggers' Diagram. Here, we add S3, the additional pulse
	which this research attempts to explore.

	W/O S3        lub..........dub.................
	With S3       lub.........dub..dub.............

	@fs int
		Sample rate of the the file
	@beatDur int
		Length of each beat?
	@tempo int   
		The tempo for the heartbeat to exist
	@pulseThree bool
		Specifies the inclusion of the S3 abnormality

	@returns [int, int] 
		Represents the filtered and unfiltered heartbeat.
	"""
	# {S3 Intensity : Amplitude Multiplier}
	s3_amplitude = {
		1: 0.003,
		2: 0.005,
		3: 0.008,
		4: 0.01,
		5: 0.02,
		6: 0.04,
		7: 0.06,
		8: 0.08,
		9: 0.1,
		10: 0.12
	}

	pulseDur = min(0.15, 0.15*beatDur)
	beatNs = floor(beatDur*fs)
	pulseNs = floor(pulseDur*fs)

	# If this heartbeat is to include S3...
	if pulseThree:

		# Volume multipliers
		loudness = [1, 0.4, s3_amplitude[pulseThree]]

		# Pause length
		timing = [0.6, 1, 0.3]

		# Variable assignment for clarity
		s1Volume, s1Pause = loudness[0], timing[0]
		s2Volume, s2Pause = loudness[1], timing[1]
		s3Volume, s3Pause = loudness[2], timing[2]

		# Template heartbeats following PCG structure
		s1Temp, s2Temp, s3Temp = singlePulse(pulseNs), singlePulse(pulseNs), singlePulse(pulseNs)

		# Multiply volumne
		s1 = [ (s1Volume * num) for num in s1Temp ]

		# Create pause
		shortPause = zeros(ceil(s1Pause * (beatNs - 2*pulseNs)))

		# Finish S2, S3
		s2 = [ (s2Volume * num) for num in s2Temp ]
		longPause = zeros(floor(s2Pause * (beatNs - 2*pulseNs)))
		s3 = [ (s3Volume * num) for num in s3Temp ]
		miniPause = zeros(ceil(s3Pause * (beatNs - 2*pulseNs)))

	else:
		loudness = [0.8, 1]
		timing = [0.25, 0.75]

		s1Volume, s1Pause = loudness[0], timing[0]
		s2Volume, s2Pause = loudness[1], timing[1]

		s1Temp, s2Temp = singlePulse(pulseNs), singlePulse(pulseNs)
		s1 = [ (s1Volume * num) for num in s1Temp ]
		shortPause = zeros(ceil(s1Pause * (beatNs - 2*pulseNs)))
		s2 = [ (s2Volume * num) for num in s2Temp ]
		longPause = zeros(floor(s2Pause * (beatNs - 2*pulseNs)))
		s3 = []
		miniPause = []

	unfilteredHeartbeat = _concatArrays([s1, shortPause, s2, miniPause, s3, longPause])
	filteredHeartbeat = _hbEQFilter(tempo, fs, unfilteredHeartbeat)

	return [filteredHeartbeat, unfilteredHeartbeat]


def singlePulse(pulseNs):
	"""
	Simulates a heartbeat _pulse_, as per the systole observed in a Wiggers'
	diagram. NOTE: this is a rough approximation, and not intended for medical
	use.

	@pulseNs int
		Number of pulses.

	@returns int
		A pulse.
	"""
	# EKG Sections
	# P
	pLength = floor((0.75 + rand()/2)*pulseNs/9)
	pAmp = (0.75 + rand()/2)*0.1
	pVec = pAmp*hanning(pLength)

	# PR segment
	prLength = floor((0.75 + rand()/2)*pulseNs/8)
	prVec = zeros(prLength)

	# Q
	qLength = floor((0.75 + rand()/2)*pulseNs/24)
	qAmp = (0.75 + rand()/2)*0.1
	qVec = -qAmp*hanning(qLength)

	# R
	rLength = floor((0.75 + rand()/2)*pulseNs/6)
	rAmp = (0.75 + rand()/2)*1
	rVec = rAmp*hanning(rLength)

	# S
	sLength = floor((0.75 + rand()/2)*pulseNs/24)
	sAmp = (0.75 + rand()/2)*0.3
	sVec = -sAmp*hanning(sLength)

	# ST segment
	stLength = floor((0.75 + rand()/2)*pulseNs/9)
	stVec = zeros(stLength)

	# T
	tLength = floor((0.75 + rand()/2)*pulseNs/9)
	tAmp = (0.75 + rand()/2)*0.2
	tVec = tAmp*hanning(tLength)

	# U
	uLength = floor((0.75 + rand()/2)*pulseNs/11)
	uAmp = (0.75 + rand()/2)*0.1
	uVec = uAmp*hanning(uLength)

	# Find the total number of samples left after adding together all
	# sections.
	sumLength = pLength + prLength + qLength + rLength + sLength + stLength + tLength + uLength

	# Remaining number of samples.
	remNs = pulseNs - sumLength

	# Silence for the remaining number of samples.
	rem = zeros(remNs)

	return _concatArrays([pVec, prVec, qVec, rVec, sVec, stVec, tVec, uVec, rem])


def _hbEQFilter(tempo, fs, unfilteredHeartbeat):
	"""
	Filters heartbeats to mimic the effect of typical heartbeat recordings
	which are taken with a microphone near the abdomen.

	@tempo int    
		The tempo for the heartbeat to exist
	@fs int
		Sample rate of the the file
	@unfilteredHeartbeat bool   
		Specifies the inclusion of the S3 abnormality

	@returns [int]
		The filtered heartbeat.
	"""
	# Butterworth 3rd order bandpass
	frequencyArray = [ x / (0.4*fs) for x in [20, 140+tempo] ]
	[bBut, aBut] = butter(3, frequencyArray, 'bandpass')

	# Peaking filter
	[bPeak, aPeak] = iirpeak((110/(fs/2)), (120/(0.5*fs)))

	# Filter the pulse to simulate an abdomen
	return lfilter(bPeak, aPeak, lfilter(bBut, aBut, unfilteredHeartbeat))


def _concatArrays(arrs):
	"""
	Mimics MATLAB array flattening behaviour.

	@arrs [[int], [int]]  
		Arbitrary 2D array.

	@returns [int]        
		All arrays, flattened.
	"""
	flattened = []
	[ flattened.extend(arrs[i]) for i in range(len(arrs)) ]
	return npArray(flattened)


def _toMP3(soundfile, remove=False): 
	"""
	Convert WAV file to mp3.

	@soundfile str
		String describing the filename.
	@remove bool
		Whether to remove the file.

	@returns None
		Outputs the audio file to the same path.
	"""
	y, sr = load(soundfile, sr=44100)
	newPath = "{}.mp3".format(soundfile[:soundfile.rfind('.')])
	output.write_wav(newPath, y, sr)

	if rmv:
		remove(soundfile)


def _createSingleBeat(filename, vol, tempoBpm=100, fs=44100, write=False):
	"""
	Helper for creating a single beat, a subset of a heartbeat. Think...only
	the LUB of the LUB DUB. This is really only for calibrating dB purposes—
	not for actual heartbeat creation, right now.

    @vol int
		Volume multiplier for the pulse
	@tempo int 
		Tempo of beat
	@fs int
		Sample rate

	@returns [int]
		Time/sound series
	"""
	beatDur = (60/tempoBpm) # 100 / MINUTE
	pulseDur = min(0.15, 0.15*beatDur)
	pulseNs = floor(pulseDur*fs)
	tempBeat = singlePulse(pulseNs)
	hb = _concatArrays([ (vol * num for num in tempBeat)])

	if write:
		audiowrite('../media/{}.wav'.format(filename), fs, hb)
		return None
	
	return hb


def _graphHbSound(s, sr):
	"""
	Helper for creating graphing a single beat in a log-power-spectogram.

    @s int
		Time/sound series, power-to-db'd
	@sr int  
		Sample rate

	@returns None
		Displays a matplot
	"""
	plt.figure()
	plt.subplot(2, 1, 2)
	display.specshow(s, sr=sr, y_axis='log', x_axis='time')
	plt.colorbar(format="%+2.0f dB")
	plt.title('Log-Power Spectogram')
	plt.tight_layout()
	plt.show()

def dbFromVol(pulseVol, task='mean', tempoBpm=100, fs=44100, writeWav=False, graph=False):
	"""
	Returns the peak dB of a given file. dB is a _relative_ unit. dBFS, 
	analogously, measures *headroom*, not absolute volume. This is useful
	for a "general estimation of comparative loudness". It essentially 
	takes an amplitude between 0 and 1 (min, max loudness respectively)

    @pulseVol int
		Volume multiplier for the pulse
	@task str
		'mean' or 'max' dBFS information
	@tempoBpm int	
		Tempo of heartbeat
	@fs int
		Sample rate
	@writeWav bool
		Do this via writing a wav file
	@graph bool	
		Display a log-power spectogram of the beat

	@returns int  
		The decibel level of the heartbeat

	Resources
	- [MIR Jupyter Resources](https://musicinformationretrieval.com/index.html)
	- [Sound determination at low frequencies](https://asa.scitation.org/doi/pdf/10.1121/1.1910763?class=pdf)
	- [`librosa` dBFS](https://librosa.github.io/librosa/generated/librosa.core.logamplitude.html)
	- [The purpose and calculation of dBFS](https://stackoverflow.com/questions/2445756/how-can-i-calculate-audio-db-level)
	- [Perceptual Weighting](https://engineersportal.com/blog/2018/9/17/audio-processing-in-python-part-ii-exploring-windowing-sound-pressure-levels-and-a-weighting-using-an-iphone-x)
	- [dB explanation](https://stackoverflow.com/questions/52943151/python-get-volume-decibel-level-real-time-or-from-a-wav-file)
	- [Equal Loudness curves](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/eqloud.html)
	- [Loudness Perception](http://www.physics.mcgill.ca/~guymoore/ph224/)
	- [Mesauring relative dB](http://neolit123.blogspot.com/2009/05/dbfs-calculator.html)
	"""
	# @todo 
	# - If this doesn't work, we could instead measure the _relative_ difference
	#    between *default* pulse and the *S3* pulse
	# - Run against each intensity level
	#    Refer to: Perceived loudness / loudness curve @ frequency
	# - Assuming perception at this volume is logarithmic...
	# - Use dB level and perceived level to make adjustments significant

	# Create S3 heartbeat
	# y = _createSingleBeat(pulseVol, tempoBpm, fs)

	if writeWav:
		audiowrite('../media/test/random.wav', fs, y)
		y, sr = load('../media/test/random.wav', sr=fs)

	# Time series manipulations
	S = np.abs(stft(pulseVol)) # y
	dBFS = power_to_db(S**2, ref=np.max)

	if graph:
		_graphHbSound(dBFS, fs)


	times = []

	if task == 'mean':
		for time in dBFS:
			mean = max(time) # sum(time) / len(time)
			
			if mean != -80:
				times.append(mean)

		return sum(times) / len(times)

	elif task == 'max':
		[times.append(max(time)) for time in dBFS]
		return max(times)

	return dBFS


def compareHb(hb1, hb2):
	"""
	"""
	pass
