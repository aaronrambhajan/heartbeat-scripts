import librosa as lb
import numpy as np
import os
import pydub as pd


def load_files(_dir):
    """
    Returns the entire directory of files with 'wav' extensions.
    """
    return [_dir+f for f in os.listdir(_dir) if
        os.path.isfile(os.path.join(_dir, f))
        and ('wav' in f)]

def toMP3(files, dirs):
    """
    Upsamples all files, then runs to mp3.

    files -> list of filenames.
        ['./sounds/regular/a0001.wav', './sounds/regular/a0003.wav'] 
    dirs -> list of target directories (original, temp, destination)
        ['./sounds/regular/', './sounds/REG/', './sounds/REGMP3']
    """
    # WAV 2K > WAV 44K > MP3 44K
    orig, temp, dest = dirs[0], dirs[1], dirs[2]

    for i in range(len(files)):

        WAV = temp + files[i].split('/')[-1] # still WAV
        MP3 = dest + files[i].split('/')[-1][:-4] + '.mp3'

        # Upsample to 44K, still .wav
        y, sr = lb.load(files[i])
        wav = lb.resample(y, sr, 44100)
        lb.output.write_wav(WAV, wav, 44100) # to new dir

        # Spit out MP3
        sound = pd.AudioSegment.from_wav(WAV) # new WAV
        sound.export(MP3, format='mp3') # rewritten as MP3


def readInfo(file, _dir):
    """
    Reads CSV information for flags about editing mp3 files,
    returns formatted information.

    'a0001.wav\t0\t36\t36\tsome additional noises in this recording \t\n'
    """
    pro = open(file, 'r')

    actions = {} # Assumes all filenames are unique
    for line in pro:
        info = line.split(sep='\t')
        # By this time, files have been process to MP3
        filename = _dir+(info[0].split('"')[-1][:-4])+'.mp3'
        flags = info[4].strip().split(' ')
        actions[filename] = flags

    return actions

        
def process(soundfile, flags, dest):
    """
    Processes soundfiles with given flags then writes to new directory.

    soundfile -> path to mp3
        './sounds/REGMP3/a0007.mp3'   
    flags -> list of strings 
        'd'   delete
        'e'   equalize (LPF 250Hz 12dB)
        't'   trim
        'x:x' trim parameters in ms
        i.e.  ['e', 't', '1000:2000']
    dest -> path to new location
        './sounds/R/a0007.mp3'
    """
    if 'd' in flags:
        return os.remove(soundfile)
    sound = pd.AudioSegment.from_mp3(soundfile)
    
    if 'e' in flags: 
        x = pd.effects.low_pass_filter(sound, 250)
        sound = pd.effects.low_pass_filter(x, 250)
        
    if 't' in flags: # Slice audio
        params = flags[flags.index('t')+1].split(':')
        if params[0] != '' and params[1] == '':
            new = sound[int(params[0]):(sound.duration_seconds*1000)]
        elif params[0] == '' and params[1] != '':
            new = sound[0:int(params[1])]
        else:
            new = sound[int(params[0]):int(params[1])]
        sound = new
        
    normed = pd.effects.normalize(sound) # Normalize ALL audio
    normed.export((dest+soundfile.split('/')[-1]), format="mp3") # already mp3


def run(constructed, built):
    """
    """
  
    rCSV, iCSV = "./reg_info.txt", "./irg_info.txt"
    r1, i1 = "./sounds/regular/", "./sounds/irregular/"
    r2, i2 = "./sounds/REGWAV/", "./sounds/IRGWAV/"
    r3, i3 = "./sounds/REGMP3/", "./sounds/IRGMP3/"
    r4, i4 = "./sounds/R/", "./sounds/I/"
    
    if not constructed: 
        regular = load_files(r1)
        irregular = load_files(i1)
        print('files loaded')

        toMP3(regular, [r1, r2, r3])
        toMP3(irregular, [i1, i2, i3])
        print('converted to mp3')
   
    if not built: 
        r_flags = readInfo(rCSV, r3)
        i_flags = readInfo(iCSV, i3)
        print('csv loaded') # {filename: [flags]}

        [process(_file, r_flags[_file], r4) for _file in r_flags]
        [process(_file, i_flags[_file], i4) for _file in i_flags]
        print('done')
            

if __name__ == '__main__':
    pass
    # run(True, False)
    # process('./sounds/IRGMP3/a0019.mp3', ['e', 't', '1000:'], './sounds/')
