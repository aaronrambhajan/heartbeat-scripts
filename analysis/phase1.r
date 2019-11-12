library(datasets)
library(plyr)
library(ggplot2)

data <- read.csv('../data/phase1.csv')

# Boolean values to binary to see accuracy
data$correct [data$correct == TRUE] <- 1
data$correct [data$correct == FALSE] <- 0
data$correct <- as.integer(data$correct)

# Add missing subject e-mail
data$mail[data$subject == 'jjg42zmpbkuve7f8hyq'] <- 'troyhands@gmail.com'

# Accuracy summary
accuracy <- ddply(data, .(subject), summarize, 
                 acc = sum(correct) / length(correct),
                 trials = length(correct),
                 mail = email[1])

# Exclude incomplete participant runs
accuracy <- accuracy[accuracy$trials == 80,] 

# Get rid of unnecessary columns
info <- subset(accuracy, select = -c(mail, trials))

# Basic stats
summary(info)



#importing Google Form
form_responses <- read.csv(file = '../data/phase1-survey.csv', header = TRUE)

form_responses$'Email.Address' [form_responses$Timestamp == '7/17/2018 13:22:18'] <- '61@macklab.com'

#merging Google Form and data summary
merged <- merge(accuracy, form_responses, 
                by.x = 'mail', by.y = 'Email.Address')

#splitting data into learning trials 
learn_trials = list() 
for (i in 1:60){
  temp = data[data$trial == i-1, ]
  learn_trials[[i]] = temp
}
learn_trials = data.frame(Reduce(rbind, learn_trials))

#splitting data into testing trials
test_trials = list()
for (i in 61:80){
  temp2 = data[data$trial == i-1, ]
  test_trials[[i]] = temp2
}
test_trials = data.frame(Reduce(rbind, test_trials)) 

#learning phase summary
summary_learn <- ddply(learn_trials, .(subject), summarize, 
                 acc = sum(correct) / length(correct),
                 trials = length(correct),
                 mail = email[1])

summary_learn <- summary_learn[summary_learn$trials == 60,]

#summary_learn$mail [summary_learn$subject == 'jjg42zmpbkuve7f8hyq'] <- 'troyhands@gmail.com'


#testing phase summary
summary_test <- ddply(test_trials, .(subject), summarize, 
                 acc = sum(correct) / length(correct),
                 trials = length(correct),
                 mail = email[1])

summary_test <- summary_test[summary_test$trials == 20,]

#summary_test$mail [summary_test$subject == 'jjg42zmpbkuve7f8hyq'] <- 'troyhands@gmail.com'


#putting summaries together 
total_summary <- rbind(summary_learn, summary_test)


# 
# Look through all of the q
# 
# scatterplot with x as subject, y as accuracies, different colours 

#plot <- ddply(summary_learn, .(acc))
ggplot(summary_learn, aes(x=subject, y=acc, colour=subject)) + geom_point() + 
  theme(legend.position="none",
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())

ggplot(summary_test, aes(x=subject, y=acc, colour=subject)) + geom_point() + 
  theme(legend.position="none",
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())

total_summary$trials [total_summary$trials == '60'] <- 'learning'
total_summary$trials [total_summary$trials == '20'] <- 'testing'
total_summary$trials <- as.factor(total_summary$trials)

ggplot(total_summary, aes(x=subject, y=acc, colour=trials)) + geom_point() + 
  theme(axis.text.x=element_blank(),axis.ticks.x=element_blank()) + ylim(0, 1)



# ggplot(avgRT,aes(x=EXPDUR,y=avgMRT,colour=ICON))+
#   geom_line()+
#   geom_errorbar(aes(ymin=avgMRT-ciRT,ymax=avgMRT+ciRT))+
#   facet_wrap(~R)
# mdlRT = lmer(MedianRT~EXPDUR*ICON+(1|SBJ),subset(test,R==1))