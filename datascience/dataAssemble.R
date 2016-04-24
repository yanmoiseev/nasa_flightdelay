dataAssemble<-function(data){
  planes = unique(data$TAIL_NUM)
  trips = 30
  row_num = 1
  k = 1
  x = matrix(0,floor(dim(data)[1]/trips),trips*2+2)
  y = matrix(0,floor(dim(data)[1]/trips),1)
  i = 1
  
  data[is.na(data$AIR_TIME),"AIR_TIME"]=0
  # print(dim(x)[1])
  while(1){
    # if there are trips left continue
    if (row_num>dim(data)[1] || (row_num+trips-1)>dim(data)[1])
      break
    starting_plane = data$TAIL_NUM[row_num]
    if (data$TAIL_NUM[row_num+trips-1]==starting_plane){
      a = stack_data(data[row_num:(row_num+trips-1),c(12,14:17)],dim(x)[2])
      x[k,] = as.numeric(a$x)
      y[k] = a$y
      k = k+1
      row_num = row_num +  trips
    }
    else { # else jump to next plane
      i = i+1
      row_num = match(planes[i],data$TAIL_NUM)
      # print(c(i,k))
    }
  }
  
  return(list(x=x[1:(k-1),],y=y[1:(k-1),]))
}

stack_data <- function(data,k){
  x <- matrix(0,k,1)
  x[1:4]<-data[1,2:5]
  x[5:k]<-c(t(as.matrix(data[2:dim(data)[1],4:5])))
  return(list(x=x[1:k],y=sum(data[,1])))
}