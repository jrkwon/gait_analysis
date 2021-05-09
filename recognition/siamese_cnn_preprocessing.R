getwd()
setwd("/home/user/Documents/workspace/First-project/recognition")
list.files()
data<-read.csv('CASIA0808(smooth6).csv')
str(data)

sort(table(data$id))

cnt <- as.character(data$id)

# cnt <- gsub('_','',cnt)


for(i in 1:length(cnt))
{
  if('3' == substr(cnt[i],6,6))
  {
    cnt[i] <- paste0(substr(cnt[i],1,5), '1')
  }
  else if('4' == substr(cnt[i],6,6))
  {
    cnt[i] <- paste0(substr(cnt[i],1,5), '2')
  }
}

sort(table(cnt))
data$id <- as.factor(cnt)
str(data)

####MERGE
data<-read.csv('CASIA0808(smooth6).csv')
str(data)
data$id
colnames(data)

df <- data.frame()
for(i in 1:(nrow(data)-1))
{
  print(c(i, '/', nrow(data)))
  for(j in (i+1):nrow(data))
  {
    df<-rbind(df, cbind(data[i,], data[j,]))
  }
}
colnames(df) <- c(paste0(colnames(df)[1:(length(colnames(df))/2)],'_left'), paste0(colnames(df)[1:(length(colnames(df))/2)],'_right'))
write.csv(df, 'siameseCNN_0822(2).csv',row.names=FALSE)
