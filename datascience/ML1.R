library(dplyr)
library(xgboost)
library(weatherData)

data$HOUR = floor((data$DEP_TIME)/100)
data$DAY = weekdays(data$FL_DATE)

# get previous hours delay by airport
cols = c("FL_DATE","ORIGIN","HOUR","DEP_DELAY","ARR_DELAY")
origin_delay = data[!is.na(data$DEP_TIME),cols]#order(data$FL_DATE,data$ORIGIN,data$HOUR)
origin_mean_delay = aggregate(origin_delay[, 4:5], origin_delay[,1:3], mean)
colnames(origin_mean_delay)[4:5]=c("OR_DEP_DELAY","OR_ARR_DELAY")

cols = c("FL_DATE","DEST","HOUR","DEP_DELAY","ARR_DELAY")
dest_delay = data[!is.na(data$DEP_TIME),cols]#order(data$FL_DATE,data$ORIGIN,data$HOUR)
dest_mean_delay = aggregate(dest_delay[, 4:5], dest_delay[,1:3], mean)
colnames(dest_mean_delay)[4:5]=c("DEST_DEP_DELAY","DEST_ARR_DELAY")

data$PREV_HOUR = data$HOUR-2
data$PREV_HOUR_DAY = data$FL_DATE
data[!is.na(data$PREV_HOUR) & data$PREV_HOUR<0,"PREV_HOUR_DAY"] = data$FL_DATE[!is.na(data$PREV_HOUR) & data$PREV_HOUR<0]-1 
data[!is.na(data$PREV_HOUR) & data$PREV_HOUR<0,"PREV_HOUR"] = 24+data[!is.na(data$PREV_HOUR) & data$PREV_HOUR<0,"PREV_HOUR"]

data = merge(data,dest_mean_delay,all=TRUE)
data = merge(data,origin_mean_delay,all=TRUE)


# #get weather data
# airports3 = read.csv("airports_latlong.csv")
# for (i in 1:length(airports3)){
#   tmp = getWeatherForDate(as.character(airports3[i,2]), "2014-12-01", "2014-12-31")
#   if (i==1)
#     weather = cbind(rep(airports3[i,2],dim(tmp)[1]),tmp)
#   else{
#     tmp = cbind(rep(airports3[i,2],dim(tmp)[1]),tmp)
#     weather = rbind(weather,tmp)
#   }
# }

data = data[order(data$FL_DATE,data$DEP_TIME),]
train_set = 1:50000
test_set = 50001:60000
data$DAY = as.factor(data$DAY)

options(na.action='na.omit')
# ,"FL_DATE","PREV_HOUR_DAY"
drop_cols = c("AIR_TIME","ARR_TIME","TAIL_NUM","ORIGIN","DEST","PREV_HOUR","PREV_HOUR_DAY")
data2 = model.matrix(~., data=data[,!colnames(data) %in% drop_cols])[,-1]

# options(na.action='na.pass')
train = list()
drop_cols2 = c("DEP_TIME","DEP_DELAY","ARR_DELAY")
train$data = data2[train_set,!colnames(data2) %in% drop_cols2]
#train$data = model.matrix(~., data=train$data)[,-1]
train$label = data2[train_set,"ARR_DELAY"]
test = list()
test$data = data2[test_set,!colnames(data2) %in% drop_cols2]
#test$data = model.matrix(~., data=test$data)[,-1]
test$label = data2[test_set,"ARR_DELAY"]

# dtrain <- xgb.DMatrix(train$data, label = train$label)
# history = xgb.cv(data = dtrain,nfold = 5, max.depth = 3, nrounds = 1000, objective = "reg:linear")

bst <- xgboost(data = train$data, label = train$label, max.depth = 5,
               eta = 1, nthread = 2, nround = 20, objective = "reg:linear",missing = NaN)
pred <- predict(bst, test$data,missing = NaN)
plot(pred,test$label)
rmse = sqrt(mean((pred-test$label)^2))
print(rmse)

# Compute feature importance matrix
importance_matrix <- xgb.importance(colnames(train$data), model = bst)
# Nice graph
xgb.plot.importance(importance_matrix[1:10,])
xgb.plot.tree(feature_names = names, model = bst, n_first_tree = 2)
plot(pred-test$label,type = "l")