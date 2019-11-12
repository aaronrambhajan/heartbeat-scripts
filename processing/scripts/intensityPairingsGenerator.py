""" 
    Thsi script creates 

"""

from random import randint, sample
import csv


_all = []
print('Create every possible pair between 1 and 10')

for i in range(1, 11):
    for j in range(1, 11):
        # No duplicates!
        if (i, j) not in _all:
            _all.append((i, j))

# Our four splits
pairs = {'7-10': [], '4-6': [], '1-3': [], '0': []}

print('Looping through each pair and categorizing')
for pair in _all:
    diff = abs(pair[1] - pair[0])
    if diff in [7, 8, 9, 10]:
        pairs['7-10'].append(pair)
    elif diff in [4, 5, 6]:
        pairs['4-6'].append(pair)
    elif diff in [1, 2, 3]:
        pairs['1-3'].append(pair)
    elif diff in [0]:
        pairs['0'].append(pair)


# The totals end up being:
# '7-10'  12
# '4-6'   30
# '1-3'   48
# '0'     10

print('Filtering pairs...')
# Make one of these true depending on which option is desired
sampling = False
psychoPy = False
even = True

# Options for handling this unevenness:

# (1) Sample 28 of 48 pairs in '1-3' `random.sample(arr, 28)`
#      which would cut it down to [12, 30, 28, 10], totalling to 80
if sampling:
    pairs['1-3'] = sample(pairs['1-3'], 28)

# (2) Keep everything and let PsychoPy make the decision randomly,
#      which would distribute cats randomly—I only suggest this bc
#      clearly I have no idea how PsychoPy works
if psychoPy:
    pass

# (3) Reduce all sections down to 10, then do it again
#      so we have a guaranteed even distribution
if even:
    new = {'7-10': [], '4-6': [], '1-3': [], '0': []}
    for section in list(pairs.keys()) + list(pairs.keys()): # want it to run twice
        new[section].extend(sample(pairs[section], 10))
    pairs = new


print("7-10: {}\n4-6: {}\n1-3: {}\n0: {}\n".format(len(pairs['7-10']), \
    len(pairs['4-6']), len(pairs['1-3']), len(pairs['0'])))


print('Mapping pairs to heartbeat strings')
filenames, correctKeyMap = [], {'7-10': 'j', '4-6': 'j', '1-3': 'j', '0': 'f'}
for section in pairs.keys():
    rng = pairs[section]
    for pair in rng:
        filenames.append(["TR_{}_v{}.wav".format(pair[0], randint(0, 7)), \
            "TR_{}_v{}.wav".format(pair[1], randint(0, 7)), \
            correctKeyMap[section]])


print('Writing to .csv file...')

csvFile = open('test.csv', 'w')
writer = csv.writer(csvFile)
writer.writerow(["whichSound", "whichSound2", "corAns"])
writer.writerows(filenames)
csvFile.close()

print('Success!')
