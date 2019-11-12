import librosa as lb
import numpy as np
import os

"""
    This script is a (futile, uninformed) attempt at detecting variation in 
    BPM for a set of real-world heartbeat samples that were used in a
    psychophysics experiment studying the perception of abnormalities in 
    heartbeats.
"""

regular = [f for f in os.listdir("../sounds/regular/") if os.path.isfile(os.path.join("./regular/", f)) and ('wav' in f)]
irregular = [f for f in os.listdir("../sounds/irregular/") if os.path.isfile(os.path.join("./irregular/", f)) and ('wav' in f)]

reg_var = []
irr_var = []
for file in regular:
    y, sr = lb.load("../sounds/regular/" + file)
    est = lb.beat.tempo(y, sr, aggregate=None)
    reg_var.append(np.var(est))

for file in irregular:
    x, rs = lb.load("../sounds/irregular/" + file)
    est = lb.beat.tempo(x, rs, aggregate=None)
    irr_var.append(np.var(est))


print(sum(reg_var) / len(reg_var))
print(sum(irr_var) / len(irr_var))
    
