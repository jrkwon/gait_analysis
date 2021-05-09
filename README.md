# Gait-analysis
openpose + 3D baseline

<hr/>

## openpose

install openpose
https://hiseon.me/2018/02/19/introduction-openpose/

and put in the Gait-analysis/openpose/

my folder structure is...

_Gait-analysis/openpose/3rdparty_

_Gait-analysis/openpose/build_

_Gait-analysis/openpose/cmake_

_._

_._


openpose controller is __Gait-analysis/openpose/main.sh__
<hr/>

## 3D-Baseline

### Gait-analysis/3d-pose-baseline/data
3D-Baseline using <a href=https://hiseon.me/2018/02/19/introduction-openpose/>Human 3.6M dataset</a>

h3.6m download <a href=wget https://www.dropbox.com/s/e35qv3n6zlkouki/h36m.zip>link</a>

if you done download, run this command <code>unzip h36m.zip</code>
and move h36m folder to Gait-analysis/3d-pose-baseline/data/h36m

### Gait-analysis/3d-pose-baseline/experiments
model directory

### Gait-analysis/3d-pose-baseline/png
save png file from 2D to 3D

### Gait-analysis/3d-pose-baseline/gif_output
save result

3D-Baseline controller is __Gait-analysis/3d-pose-baseline/main.sh__
<hr/>

## Gait-analysis/

__input video directory is <code>Gait-analysis/video</code>__
__output directory is <code>Gait-analysis/output</code>__

### Gait-analysis/output/\<filename\>/openpose/
save openpose result (frame -> people -> joint -> x,y,c)

### Gait-analysis/output/\<filename\>/3d-baseline/
save 3d-baseline result (3d joint info)

this project master controller is __Gait-analysis/main.sh__

<hr/>

## Dataset -> MARS

we concatenate MARS dataset each id .jpg to .mp4
and select one person video.

Mart dataset best walking id list (#42)
2, 4, 60, 100, 104, 142, 158, 198, 202(front), 316,322, 378, 386, 426, 430, 432, 500, 610, 636, 646,650, 670, 686, 762(front), 776, 792, 824, 868, 904, 916,918, 992, 1016, 1026, 1112(end), 1158(mid), 1182, 228, 1270, 1318, 1372(front), 1480

<hr/>

we prepared Video(MARS) calculaste to 3D joint value.
this info. save the _recognition/feature.csv_ and _recognition/main.py_ call this csv file.

preprocessing
1. get gait cycle
2. if you use the option(remove outlier, calculate DTW distance) turn on the process value.
3. select the feature and calculate and save .csv
4. classification using the .csv file -> ing...
