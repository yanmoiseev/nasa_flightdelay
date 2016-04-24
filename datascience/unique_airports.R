b = as.character(unique(data$ORIGIN))
a = as.character(unique(data$DEST))
ports = as.data.frame(unique(c(a,b)))
colnames(ports) = "airport"
ports = merge(ports,airports,by.x = "airport",by.y = "iata")
write.csv(ports,"airports_latlong.csv")

#mock data 1 - per airport
a = cbind(ports,runif(dim(ports)[1])*10-4)
colnames(a)[4] = "delay"
k_x = kmeans(a[,3:4],52,100)
b = cbind(k_x$centers,runif(52)*10-4)
colnames(b)[3] = "delay"
write.csv(a,"mockdata1.csv")
write.csv(b,"mockdata2.csv")