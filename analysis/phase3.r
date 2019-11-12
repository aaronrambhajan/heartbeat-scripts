library(plyr)
library(ggplot2)
library(lme4)
library(lmerTest)
library(multcomp)
library(tidyr)
library(psycho)

PATH <- '../data/e3/'
filenames <- list.files(path=PATH, full.names = TRUE)
all_phase1 <- data.frame()
all_phase2 <- data.frame()
all_phase3 <- data.frame()

csThatMatterJND1 <- c("whichSound", "whichSound2", "corAns", "JND1.thisN", 
                     "key_resp_2.keys", "key_resp_2.corr", "key_resp_2.rt", "SBJ",
                     "phase")
csThatMatterLearning <- c("whichSound", "corAns", "learning_trials.thisTrialN",
                          "resp.keys", "resp.corr", "resp.rt", "SBJ", "phase")
csThatMatterJND2 <- c("whichSound", "whichSound2", "corAns", "JND2.thisN",
                      "key_resp_2.keys", "key_resp_2.corr", "key_resp_2.rt", "SBJ",
                      "phase")

for (i in 1:length(filenames)) {
  pData <- data.frame(read.csv(filenames[i]))
  pData$SBJ <- i
  
  # Split by phase
  phase1 <- subset(pData, JND1.thisN <= 79) 
  phase2 <- subset(pData, learning_trials.thisTrialN <= 79)
  phase3 <- subset(pData, JND2.thisN <= 79) 
  
  # Meaningfully mark the phase
  phase1$phase <- 1
  phase2$phase <- 2
  phase3$phase <- 3
  
  # Get rid of junk columns
  phase1 <- phase1[,csThatMatterJND1]
  phase2 <- phase2[,csThatMatterLearning]
  phase3 <- phase3[,csThatMatterJND2]
  
  # Bind
  all_phase1 <- rbind(all_phase1, phase1)
  all_phase2 <- rbind(all_phase2, phase2)
  all_phase3 <- rbind(all_phase3, phase3)
}

# Rename columns
names(all_phase1) <- c('SOUND', 'SOUND2', 'ANS', 'TRIAL', 'RESP', 'CORR', 'RT', 'SBJ', 'PHASE')
names(all_phase2) <- c('SOUND', 'ANS', 'TRIAL', 'RESP', 'CORR', 'RT', 'SBJ', 'PHASE')
names(all_phase3) <- c('SOUND', 'SOUND2', 'ANS', 'TRIAL', 'RESP', 'CORR', 'RT', 'SBJ', 'PHASE')

# Format to character for substringing
char1A <- as.character(all_phase1$SOUND)
char2A <- as.character(all_phase1$SOUND2)
char1B <- as.character(all_phase3$SOUND)
char2B <- as.character(all_phase3$SOUND2)

# Substring like spoderman
is1 <- strsplit(char1A, '_')
is2 <- strsplit(char2A, '_')
is3 <- strsplit(char1B, '_')
is4 <- strsplit(char2B, '_')

con1 <- c()
con2 <- c()
con3 <- c()
con4 <- c()

# Isolating levels 
for (i in 1:length(is1)) {
  con1 <- c(con1, is1[[i]][2])
  con2 <- c(con2, is2[[i]][2])
  con3 <- c(con3, is3[[i]][2])
  con4 <- c(con4, is4[[i]][2])
}

# Integerize to get differences
vectorOfDifferences <- abs(as.integer(con1) - as.integer(con2))
vectorOfDifferences2 <- abs(as.integer(con3) - as.integer(con4))
# Bin the values based on the mapping: 
#   {'7-10': 4, '4-6': 3, '1-3': 2, '0': 1}
vectorOfDifferences [vectorOfDifferences == 0] <- 'bin1'
vectorOfDifferences [vectorOfDifferences >= 1 & vectorOfDifferences <= 3] <- 'bin2'
vectorOfDifferences [vectorOfDifferences >= 4 & vectorOfDifferences <= 6] <- 'bin3'
vectorOfDifferences [vectorOfDifferences >= 7 & vectorOfDifferences <= 9] <- 'bin4'

vectorOfDifferences2 [vectorOfDifferences2 == 0] <- 'bin1'
vectorOfDifferences2 [vectorOfDifferences2 >= 1 & vectorOfDifferences2 <= 3] <- 'bin2'
vectorOfDifferences2 [vectorOfDifferences2 >= 4 & vectorOfDifferences2 <= 6] <- 'bin3'
vectorOfDifferences2 [vectorOfDifferences2 >= 7 & vectorOfDifferences2 <= 9] <- 'bin4'

all_phase1['BIN'] <- NA
all_phase1$BIN <- vectorOfDifferences
all_phase1['PHASE'] <- 1

all_phase3['BIN'] <- NA
all_phase3$BIN <- vectorOfDifferences2
all_phase3['PHASE'] <- 3

phase1analysis <- ddply(all_phase1, .(BIN, SBJ, PHASE), summarize, acc = round(sum(CORR) / length(CORR), 4))
phase3analysis <- ddply(all_phase3, .(BIN, SBJ, PHASE), summarize, acc = round(sum(CORR) / length(CORR), 4))

#JND data to plot
JND <- rbind(phase1analysis, phase3analysis)

#plot JND data
ggplot(JND, aes(BIN, acc, fill=factor(PHASE))) + geom_violin(scale='area') + 
  geom_dotplot(binaxis='y', position=position_dodge(1), stackdir='center', dotsize=0.50)

#phase 2 
glmer(CORR~TRIAL + (1|SBJ), data=all_phase2, family=binomial)
#what does this mean?

#signal detection theory - d' phase 1
signalDetectionData <- data.frame(SBJ = c(all_phase1$SBJ),
                                  n_hit = as.integer(as.logical(c(all_phase1$BIN != 'bin1' & all_phase1$CORR == 1))),
                                  n_miss = as.integer(as.logical(c(all_phase1$BIN != 'bin1' & all_phase1$CORR == 0))),
                                  n_fa = as.integer(as.logical(c(all_phase1$BIN == 'bin1' & all_phase1$CORR == 0))),
                                  n_cr = as.integer(as.logical(c(all_phase1$BIN == 'bin1' & all_phase1$CORR == 1))))
# n_hit and n_fa needs to be probabilities, so divide by # times it was whatever bin
dprime <- qnorm(signalDetectionData$n_hit) - qnorm(signalDetectionData$n_fa) # I don't think this is right - change to probability 

#calculate d' for each bin as well, bin4 hits should be better than bin2 
