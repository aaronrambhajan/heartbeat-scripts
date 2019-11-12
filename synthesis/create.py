"""
Suite of functions for the synthesis of heartbeats. Adapted and inspired
by [Ben C. Holmes'](https://github.com/bencholmes/heartbeat) MATLAB script.
"""

from functions import makeHeartbeats, _createSingleBeat, _toMP3, dbFromVol, processEffects
from matplotlib import pyplot as plt
from pysndfx import AudioEffectsChain
from glob import glob
from random import randint

"""
    Creates heartbeat sounds!

    @filename     (str)  Name of the file                        default="python_heartbeat"
    @numBeats     (int)  The number of beats in the recording    default=10
    @tempoBpm     (int)  The tempo of the heartbeat              default=100
    @fs		      (int)  Sample rate, default is                 default=44100
    @includeThird (int)  Specifies the volume of S3. Defaults 	 default=0 || 5*
                        to 0 (meaning no S3), otherwise,
                        takes a value between 1 and 10 where 5*
                        is the default.

    returns  	  (None) Outputs an audiofile to the filename.

    >>> makeHeartbeats(tempoBpm=80, filename="calibration")
    >>> makeHeartbeats(tempoBpm=90, includeThird=10, filename="heartbeat_sound")
"""

def createSamples(numVersions):

    # Generate the base files
    for intensity in range(1, 11):
        makeHeartbeats(tempoBpm=80, numBeats=10, includeThird=intensity, filename="base/HB_S3_{}".format(intensity), write=True)
        _createSingleBeat("base/TR_{}".format(intensity), intensity, tempoBpm=80, write=True)

    # Create different versions of each base sample
    baseSounds = glob("../media/base/*.wav", recursive=True)
    print('{} base sounds written'.format(len(baseSounds)))

    for version in range(1, numVersions+1):

        # Randomize effects
        fx = (
            AudioEffectsChain()
            .reverb(reverberance=randint(0, 30), 
                    hf_damping=randint(0, 30), 
                    room_scale=randint(0, 30), 
                    stereo_depth=randint(0, 30))
            .pitch(shift=randint(-300, 300))
            )

        # Apply effects to each intensity and write new file
        for sound in baseSounds:
            new = "../media/main/{}_v{}.wav".format(sound[sound.rfind('/'):sound.rfind('.')], version)
            
            # Write new sound
            fx(sound, new)  
        
        print('Version {} sounds written'.format(version))

    # Rewrite all files to WAV
    # newSounds = glob("../media/main/*.wav", recursive=True)
    # [ _toMP3(soundfile, rmv=True)for soundfile in newSounds ]
    # [ _toMP3(soundfile, rmv=True) for soundfile in baseSounds ]


if __name__ == '__main__':
    createSamples(7)



    # makeHeartbeats(tempoBpm=80, numBeats=1, includeThird=1)
    # makeHeartbeats(tempoBpm=80, numBeats=1, includeThird=10)
    # for i in range(1, 11):
    #     x.append(makeHeartbeats(tempoBpm=80, numBeats=1, includeThird=i))
    
    # plt.plot(x)
    # plt.ylabel('avg. amplitude')
    # plt.show()
    # print(dbFromVol(0.12, 'mean'), dbFromVol(1, 'mean'))
