setwd('~/Documents/Hackathon/SpaceApps delays/')
source('~/Documents/Hackathon/SpaceApps delays/dataAssemble.R')
delays = read.csv("2014_dec.csv")
#library(ggmap)
#library(rstan)
# rstan_options(auto_write = TRUE)
# options(mc.cores = parallel::detectCores())


dests_unique = unique(delays$DEST)
dests_unique = paste(dests_unique,"airport")
# dests_unique_loc = geocode(dests_unique)
# dests_unique_loc2 = geocode(dests_unique, source = "dsk")
# 
# concat_dests = paste(dests_unique_loc$lat,dests_unique_loc$lon)

airports =  read.csv("airports.csv")
features = c("FL_DATE","UNIQUE_CARRIER","TAIL_NUM","ORIGIN","DEST",
             "CRS_DEP_TIME","DEP_TIME","DEP_DELAY","CRS_ARR_TIME",
             "ARR_TIME","ARR_DELAY","AIR_TIME","DISTANCE")
data = delays[,features]

# Claen data and get lat longs
data$FL_DATE = as.Date(data$FL_DATE)
airports =  airports[,c("iata","lat","long")]
data = merge(data,airports,by.x = "ORIGIN", by.y = "iata")
colnames(data)[14] = "ORIGIN_LAT"
colnames(data)[15] = "ORIGIN_LONG"
data = merge(data,airports,by.x = "DEST", by.y = "iata")
colnames(data)[16] = "DEST_LAT"
colnames(data)[17] = "DEST_LONG"

#clear stuff without tail num
data = data[data$TAIL_NUM!="",]

#order data by tailnum date and dep time
data = data[order(data$TAIL_NUM,data$FL_DATE,data$DEP_TIME),]
x_set = dataAssemble(data)

# plane_dat <- list(N = dim(x_set$x)[1], 
#                     D = dim(x_set$x)[2],
#                     M = dim(x_set$x)[2],
#                     x = x_set$x,
#                     y = x_set$y)

#m <- stan_model(file="cluster.stan")
#f <- vb(m,plane_dat,iter=30000,tol_rel_obj=1e-4)
#la <- extract(f, permuted = TRUE) # return a list of arrays 
#mu <- la$