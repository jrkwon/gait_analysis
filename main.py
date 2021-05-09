import os
import sys
from shutil import copyfile
from time import localtime, strftime
import subprocess
import argparse

def main(video_path, file_name, openpose_flag):
    #openpose_flag = True #jkwon False
    baseline_flag = not openpose_flag #True #False
    fileremove_flag = False

    # #openpose 
    if(openpose_flag):
        openpose ="""cd ./openpose/ && ./main.sh {0} {1}"""
        # cur_time = strftime("%y%m%d_%H%M%S", localtime())
        # output_path = '../output/' + cur_time + '/openpose/'
        output_path = '../output/' + file_name + '/openpose/'
        print(output_path)
        os.mkdir('./output/' + file_name)
        openpose = openpose.format(video_path, output_path)
        print("======================================================")
        print("=======================OPENPOSE=======================")
        print("=======================DISPLAY========================")
        print("======================================================")
        subprocess.check_output(['bash','-c',openpose])
        #/home/jaerock/Documents/openpose/build/examples/openpose/openpose.bin --video examples/media/walking.ogv --write_json json_output


    #setting output_path
    if(openpose_flag is False):
        # file_name = os.listdir('./output/')
        # file_name.sort()
        # output_path = '../output/' + file_name[-1] + '/openpose/'
        output_path = '../output/' + file_name + '/openpose/'
        # os.mkdir('./output/' + file_name)
        # os.mkdir('./output/' + file_name + '/openpose/')

    # #3D baseline
    if(baseline_flag):
        baseline = 'cd ./3d-pose-baseline/ && ./main.sh {0}'.format(output_path)
        print("======================================================")
        print("=======================BASELINE=======================")
        print("======================================================") 
        print(baseline)
        subprocess.check_output(['bash','-c',baseline])
        print("result file path : ./3d-pose-baseline/gif_output/animation.gif")
        print("result file path : ./3d-pose-baseline/png")
        copyfile(gif_path, './mars/3d_handmade/'+file_name+'.gif')

    #remove json file (openpose result) ???
    if(fileremove_flag):
        print("================REMOVE OPENPOSE *.json================")
        subprocess.check_output(['bash','-c', 'rm -rf '+'./output/' + file_name +'/openpose/'] )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", help="run openpose or baseline")
    args = parser.parse_args()
    
    openpose_flag = True if args.run == 'openpose' else False

    mp4_path = './video/' # input video path
    # mp4_path = '/home/user/Downloads/CASIA Dataset A/surveillance.idealtest.org/CASIA-Dataset-A/gaitdb_mp4/'
    gif_path = './3d-pose-baseline/gif_output/animation.gif'
    #dst = './temp/temp.mp4'
    
    file_names = sorted(os.listdir(mp4_path))
    
    # openpose_output_path = './output/'
    # file_names = sorted(os.listdir(openpose_output_path))
    # file_names = [f for f in file_names if not '3d-baseline' in os.listdir(openpose_output_path + f)]

    # file_names = ['fyc-90_1-001.mp4']

    for file_name in file_names:
        src = '.' + mp4_path + file_name  
        
        try:
            main(src, file_name, openpose_flag)
        except subprocess.CalledProcessError as e:
            continue
            # sys.exit(1)
        except IndexError as e:
            continue
            # os.remove(src)
            # sys.exit(1)
        except Exception as e: 
            continue
            # sys.exit(1)
        # finally:
            # copyfile(gif_path, './mars/3d_handmade/'+file_name[:-4]+'.gif')
            # os.remove(src)
        # os.remove(dst)cert0178
