library(plyr)
library(ggplot2)
library(lme4)
library(lmerTest)
library(multcomp)

# https://fathomless-spire-44257.herokuapp.com/api/get_response
data <- read.csv('../data/phase2.csv')

# Reformatting and cleaning
data$correct [data$isCorrect == TRUE] <- 1
data$correct [data$isCorrect == FALSE] <- 0
data$correct <- as.integer(data$isCorrect)
data$correct <- as.factor(data$correct)
data <- subset(data, select = -c(X_id, X__v, X))

# Summary
all_summary <- ddply(data, .(subject), summarize, 
                 acc = round(sum(isCorrect) / length(isCorrect), 4),
                 trials = length(isCorrect))

# Removing all incomplete instances
toRemove <- subset(all_summary, trials != 30)
data <- data[ !(data$subject %in% toRemove$subject), ]

# Summary of all fully completed experiments
summary <- ddply(data, .(subject), summarize, 
                acc = round(sum(isCorrect) / length(isCorrect), 4),
                trials = length(isCorrect))

# Split the 2nd and 1st editions
e2_subjects<- subset(summary, grepl('EDITION2', subject))$subject
e1_data <- data[ !(data$subject %in% e2_subjects), ]
e2_data <- data[ data$subject %in% e2_subjects, ]

# Summarize 2nd and 1st editions
e1_summary <- ddply(e1_data, .(subject), summarize, 
                 acc = round(sum(isCorrect) / length(isCorrect), 4),
                 trials = length(isCorrect))

e2_summary <- ddply(e2_data, .(subject), summarize, 
                    acc = round(sum(isCorrect) / length(isCorrect), 4),
                    trials = length(isCorrect))


# Plot e1 density
e1_plot <- smoothScatter(e1_data$trial, e1_data$intensity, main='Distribution of Responses Across All Subjects', 
                         xlab='trial', ylab='intensity', ylim=c(0,10))

# Plot e2 lines
e2_plot <- ggplot(e2_data, aes(x=trial, y=intensity, colour=subject)) + geom_line()

ggplot(e2_data, aes(x=trial, y=intensity, colour=subject)) + geom_line()

# analysis lite ®
# Check last 10 trials
e1_last10 <- subset(e1_data, trial > 20)
ddply(e1_last10, .(subject), summarize, 
                     acc = round(sum(isCorrect) / length(isCorrect), 4),
                     trials = length(isCorrect))


# Testing lmer stuff the goddess Melisa suggested
test <- subset(e1_data, subject=='jmc4xcq72qjzsru9q5a')
ggplot(test, aes(x=trial, y=intensity, colour=correct)) + geom_point()
model <- lm(intensity ~ correct, data=test)
