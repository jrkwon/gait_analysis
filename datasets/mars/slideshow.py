import cv2
import os

def get_top_frame_id(path):
    folders = os.listdir(path)
    cnt = {}
    not_frame_num = slice(0,11)

    for folder in folders:
        os.chdir(path + folder)
        jpg_files = os.listdir()
        for f in jpg_files:
            if not f[not_frame_num] in cnt.keys():
                cnt[f[not_frame_num]]=1
            else:
                cnt[f[not_frame_num]]+=1          
        os.chdir('../../')
    return(cnt)

def get_files(path, file_name):
    os.chdir(path)
    files = []
    for dirlist in os.listdir():
        if file_name in dirlist:
            files.append(dirlist)
    files = sorted(files)
    return(files)

def make_mp4(image_path, output):
    frame = cv2.imread(image_path[0])
    cv2.imshow('video', frame)
    height, width, channels = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output, fourcc, 20.0, (width, height))

    for img in image_path:
        frame = cv2.imread(img)
        out.write(frame)
        cv2.imshow('video', frame)

        if(cv2.waitKey(1) & 0xFF) == ord('q'):
            break
    out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # path = './bbox_test/'
    path = './bbox_train/'
    cnt = get_top_frame_id(path)
    file_id = slice(0,4)
    for dictionary in sorted(cnt.items(), key=lambda x: x[1])[-500:]:
        print(dictionary)
        jpglist = get_files(path + dictionary[0][file_id], dictionary[0])
        make_mp4(jpglist, '../../'+dictionary[0]+'.mp4')        
        os.chdir('../../')

    # print(folders)