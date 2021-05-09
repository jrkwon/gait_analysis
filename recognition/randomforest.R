## random forest

getwd()
setwd("/home/user/Documents/workspace/First-project/recognition")

list.files()
data<-read.csv('CASIA0808(smooth6).csv')
str(data)
colnames(data)[1] <-'target_id'

data[,1] <- factor(substr(as.character(data[,1]), 1, 4))


labels <- unique(data[,1])

## remove outlier
# baseline: boxplot & period
remove_outlier<-c()
for(target_id in labels)
{
  target_data <- data[data[1]==target_id,]
  info <- summary(target_data$period)
  iqr <- info["3rd Qu."] - info["1st Qu."]
  limit_min <- info["1st Qu."] - iqr*1.5
  limit_max <- info["3rd Qu."] + iqr*1.5
  index <- ! (limit_min > data[data[1]==target_id, "period"] | limit_max < data[data[1]==target_id, "period"])
  remove_outlier <- rbind(remove_outlier, target_data[index,])
}

## random forest
library(randomForest)
library(MASS)
library(reprtree)


model_data <- remove_outlier
model_data <- model_data[,-which(colnames(model_data) == "upper_body")]
model_data <- model_data[,-which(colnames(model_data) == "right_lower_leg")]
model_data <- model_data[,-which(colnames(model_data) == "right_upper_leg")]
model_data <- model_data[,-which(colnames(model_data) == "left_lower_leg")]
model_data <- model_data[,-which(colnames(model_data) == "left_upper_leg")]



#################### SVM & Random Forest ####################
# library(ipred)
# library(e1071)
# error.RF <- numeric(10)
# error.SVM <- numeric(10)

# tune(randomForest, target_id ~., data=model_data, range=list(mtry=c(4,5,6,7), ntree=c(500,600,750,1000)), importance=TRUE)
# for(i in 1:10) error.RF[i] <- errorest (target_id ~ ., data=model_data, model=randomForest, mtry = 7, ntree=750)$error
# summary(error.RF)

# tune(svm, target_id ~., data=model_data, kernel='linear', range=list(gamma=c(0.1, 0.25, 0.5, 0.75, 1, 2, 3, 4), cost=2^(2:5)))
# for (i in 1:10) error.SVM[i] <-errorest(target_id ~ ., data = model_data, model = svm, cost = 8, gamma = 0.1)$error
# summary(error.SVM)


################## train, test ##################
library(caret)
error.RF <- numeric(10)
inTrain <- createDataPartition(y = model_data[,1], p = 0.7, list = F)
# scalable <- scale(model_data[-1])
# train <- as.data.frame(cbind(model_data[inTrain,1], scalable[inTrain,]))
# test <- as.data.frame(cbind(model_data[-inTrain,1], scalable[-inTrain,]))
train <- model_data[inTrain,]
test <- model_data[-inTrain,]
table(train[,1])
table(test[,1])

tune(randomForest, target_id ~., data=train, range=list(mtry=c(4,5,6,7,8), ntree=c(250,400,500,600,750,1000)), importance=TRUE)
# from tune, we get the bset mtry, ntree values.

## exec line by line
for(i in 1:10) error.RF[i] <- errorest(target_id ~ ., data=train, model=randomForest, mtry =6, ntree=750)$error
summary(error.RF)

gait.rf <- randomForest(target_id ~ ., data = train, mtry = 6, ntree = 750, importance = TRUE)
print(gait.rf)
importance(gait.rf)
varImpPlot(gait.rf)

prediction <-predict(gait.rf, test)
confusionMatrix(prediction, test$target_id)
