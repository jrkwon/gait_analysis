getwd()
setwd('//media//jaerock//My Passport//gait-analysis//output')

install.packages('jsonlite')
library(jsonlite)
install.packages('stringr')
library(stringr)

dir <- list.files()
# dir <- dir[substr(dir, nchar(dir)-3, nchar(dir))==".csv"]
# dir <- dir[0:184]
# id_list <- c(2, 4, 60, 100, 104, 142, 158, 198, 316, 322, 378, 386, 426, 430, 432, 500, 610, 636, 646, 650, 670, 686, 776, 792, 824, 868, 904, 916, 918, 992, 1016, 1026, 1182, 1228, 1270, 1318, 1480)
# 
# file_list <- NULL
# file_list <- c(file_list, dir[substr(dir, 0, 4) == '1112'][2])
# file_list <- c(file_list, dir[substr(dir, 0, 4) == '1158'][2])
# file_list <- c(file_list, dir[substr(dir, 0, 4) == '0762'][1])
# file_list <- c(file_list, dir[substr(dir, 0, 4) == '0202'][1])
# file_list <- c(file_list, dir[substr(dir, 0, 4) == '1372'][1])

for(f in id_list)
{
  print(f)
  file_list <- c(file_list, dir[unlist(lapply(substr(dir,0,4), as.integer))==f])
}


cnt <- 0
for(name in dir)
{
  data <- matrix(ncol=21)
  colnames(data) <- c("id", "angle", "frameNum", "x, y, z", "Head", "LShoulder", "Neck.Nose", "Spine", "Thorax", "RFoot", "RShoulder", "LElbow", "LWrist", "LFoot", "RKnee", "RElbow", "LKnee", "LHip", "RHip", "Hip", "RWrist")
  
  cnt = cnt+1
  print(paste0('[', cnt, '/', length(dir), '] ', name, '...'))
  if(any('3d-baseline' == list.files(name)))
  {
    jsons <- list.files(paste0(name,'/3d-baseline'))
    for(json in jsons)
    {
      frameNum <- as.integer(gsub('[^0-9]','', json))
      pannel <- rbind( cbind(substr(name, 1, 4), substr(name, 6, 6), frameNum, 'x'),
                       cbind(substr(name, 1, 4), substr(name, 6, 6), frameNum, 'y'),
                       cbind(substr(name, 1, 4), substr(name, 6, 6), frameNum, 'z'))
      colnames(pannel) <- c('id', 'angle', 'frameNum', 'x, y, z')
      
      temp <- fromJSON(paste0(name,'/3d-baseline/', json))
      temp <- data.frame(temp)
      temp <- cbind(pannel, temp)
      
      data <- rbind(data, temp)
    }
    data <- data[-1,]
    write.csv(data, file = paste0(name,'.csv'), row.names = FALSE)
  }
}

### merge ###
csv_files <- file_list
csv_files <- sort(csv_files)
merge_data <- NA
for(csv in csv_files)
{
  if(nchar(csv)==15)
  {
    temp <- read.csv(csv, header=TRUE)
    merge_data <- rbind(merge_data, temp)
  }
}
merge_data <- merge_data[-1,]
write.csv(merge_data, file = 'merge_MARS.csv', row.names = FALSE)
