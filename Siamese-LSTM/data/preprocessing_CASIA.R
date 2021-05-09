getwd()
setwd('/media/jaerock/My Passport/gait-analysis/output')

list.files()

data <- read.csv('merge_CASIA_test.csv', header = TRUE)
# data[,-2]
# str(data)


colnames(data[])[5:21]

# setting colnames
my_colnames <- c('id', 'frame')
my_colnames <- c(my_colnames, paste0('x_', colnames(data[])[5:21]))
my_colnames <- c(my_colnames, paste0('y_', colnames(data[])[5:21]))
my_colnames <- c(my_colnames, paste0('z_', colnames(data[])[5:21]))


mat <- matrix(ncol = length(my_colnames))
colnames(mat) <- my_colnames

df <- as.data.frame(mat)
id <- unique(as.character(data[,1]))

for(i in 1:length(id))
{
  print(c(i, '/', length(id)))
  id_data <- data[id[i]==data[,1],]
  for(j in seq(1,nrow(id_data),3))
  {
    row <- cbind(id_data[j,-c(2,4)], id_data[j+1,-c(1:4)], id_data[j+2,-c(1:4)])
    colnames(row) <- my_colnames
    df <- rbind(df,row)
  }
}

df <- df[-1,]
setwd('/media/jaerock/My Passport/gait-analysis/Siamese-LSTM/data')
write.csv(df, 'siamese.csv', row.names = FALSE)

############################
# make paddings to make pairs

# 127 --> the max video frame number in the dataset. (CASIAA)
max_frame <- 127

data <- read.csv('siamese.csv', stringsAsFactors = F)
str(data)
colnames(data)
data <- data[c('id','x_RFoot','x_LFoot','x_RKnee','x_LKnee','x_LHip','x_RHip',
       'y_RFoot','y_LFoot','y_RKnee','y_LKnee','y_LHip','y_RHip',
       'z_RFoot','z_LFoot','z_RKnee','z_LKnee','z_LHip','z_RHip')]
# data[,1] <- as.character(data[,1])

# remove 90
data <- data[substr(gsub('[a-z]','',data[,1]),1,2) != '90',]
id_list <- unique(as.character(data$id))

mat <- matrix(ncol = 38)
colnames(mat) <- c(paste0(colnames(data), '_1'), paste0(colnames(data), '_2'))

for(idx1 in 1:(length(id_list)-2))
{
  print(id_list[idx1])
  for(idx2 in (idx1+1):length(id_list))
  {
    temp_1 <- data[data$id == id_list[idx1],]
    temp_2 <- data[data$id == id_list[idx2],]
    if((max_frame - nrow(temp_2)) > 0)
    {
      zero <- matrix(nrow = max_frame - nrow(temp_2), ncol = ncol(temp_2))
      colnames(zero) <- colnames(temp_2)
      zero <- data.frame(zero, stringsAsFactors = F)
      zero[,1] <- id_list[idx2]
      zero[is.na(zero)] <- as.numeric(0)
      temp_2 <- rbind(zero, temp_2)
    }
    if((max_frame - nrow(temp_1)) > 0)
    {
      zero <- matrix(data = 0, nrow = max_frame - nrow(temp_1), ncol = ncol(temp_1))
      colnames(zero) <- colnames(temp_1)
      zero[,1] <- id_list[idx1]
      zero <- data.frame(zero, stringsAsFactors = F)
      temp_1 <- rbind(zero, temp_1)
    }
    colnames(temp_1) <- paste0(colnames(temp_1), '_1')
    colnames(temp_2) <- paste0(colnames(temp_2), '_2')
    mat <- rbind(mat, cbind(temp_1, temp_2))
  }
}
mat <- mat[-1,]
write.csv(mat, 'preprocessing_siamese127_test.csv',, row.names = FALSE)
