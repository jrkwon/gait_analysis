getwd()
setwd('//media//jaerock//My Passport//gait-analysis//output')

# install.packages('jsonlite')
library(jsonlite)
# install.packages('stringr')
library(stringr)
dir <- list.files()

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
      id <- paste0(unlist(str_split(name,'-'))[1], unlist(str_split(name,'-'))[2]) #fyc00_1 #subjectIDviewPointAngle
      angle <- unlist(str_split(unlist(str_split(name,'-'))[2],'_'))[1] #00 #viewPointAngle
      pannel <- rbind( cbind(id, angle, frameNum, 'x'),
                       cbind(id, angle, frameNum, 'y'),
                       cbind(id, angle, frameNum, 'z'))
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
csv_files <- list.files()
csv_files <- csv_files[substring(csv_files,17,20) == "csv" | substring(csv_files,17,20) == ".csv"]


csv_files <- file_list
#csv_files <- c("fyc-00_1-001.mp4.csv","fyc-00_3-001.mp4.csv","hy-00_1-001.mp4.csv","ljg-00_1-001.mp4.csv", "lqf-00_3-001.mp4.csv", "rj-00_1-001.mp4.csv","rj-00_3-001.mp4.csv",  "syj-00_1-001.mp4.csv",  "wl-00_3-001.mp4.csv",  "wq-00_3-001.mp4.csv",  "wyc-00_1-001.mp4.csv",  "yjf-00_3-001.mp4.csv",  "zdx-00_1-001.mp4.csv",  "zdx-00_3-001.mp4.csv",  "zjg-00_1-001.mp4.csv",  "zjg-00_3-001.mp4.csv")
csv_files <- sort(csv_files)
merge_data <- NA
for(csv in csv_files)
{
  temp <- read.csv(csv, header=TRUE, col.names = c("id", "angle", "frameNum", "x, y, z", "Head", "LShoulder", "Neck.Nose", "Spine", "Thorax", "RFoot", "RShoulder", "LElbow", "LWrist", "LFoot", "RKnee", "RElbow", "LKnee", "LHip", "RHip", "Hip", "RWrist"))
  merge_data <- rbind(merge_data, temp)
}
merge_data <- merge_data[-1,]
write.csv(merge_data, file = 'merge_CASIA_test.csv', row.names = FALSE)
