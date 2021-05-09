import csv
import numpy as np
from scipy.interpolate import CubicSpline

joint_name = ['id','camera','frameNum','xyz','Head', 'LShoulder', 'Neck.Nose', 'Spine', 'Thorax', 'RFoot', 'RShoulder', 'LElbow', 'LWrist', 'LFoot', 'RKnee', 'RElbow', 'LKnee', 'LHip', 'RHip', 'Hip', 'RWrist']


def read_data(filename, ret = False):
    global data, indexing
    data = []
    indexing = {}
    print('='*10, 'READ CSV', '='*10)
    with open(filename, 'r', encoding = 'utf-8', newline='') as csvfile:
        rows = csv.reader(csvfile)
        for i, row in enumerate(rows):
            data.append(row)
            if row[0] in indexing.keys():
                indexing[row[0]]['length'] += 1
            else:
                indexing[row[0]] = {'start':i, 'length':1}
    if ret==True:
        return data
    return None


def get_id_list():
    return list(set([x[0] for x in data]))


def get_joint_slice(part):
    return joint_name.index(part)


def get_slice(num):
    num = str(num)
    start = indexing[num]['start']
    end = start + indexing[num]['length']
    return slice(start,end)


def data_interpolation(val_list, multi):
    import pandas as pd
    #interpolation
    inter = CubicSpline(range(len(val_list)), val_list)
    return(inter(np.arange(0,len(val_list), 1/multi)))


def get_id_frameNum(target_id, frameNum):
    s = get_slice(target_id)
    start = s.start + (frameNum * 3)
    return data[start:start+3]


def distance(a,b):
    return(np.linalg.norm(np.array(a)-np.array(b)))


def head_foot_distances(target_id):
    temp = data[get_slice(target_id)]
    
    right_ret = []
    left_ret = []

    head = get_joint_slice('Head')
    rfoot = get_joint_slice('RFoot')
    lfoot = get_joint_slice('LFoot')
    for i in range(0, len(temp), 3):
        h = []
        r = []
        l = []
        for j in range(2): ## x,y
            h.append(float(temp[i+j][head]))
            r.append(float(temp[i+j][rfoot]))
            l.append(float(temp[i+j][lfoot]))
        right_ret.append(distance(h,r))
        left_ret.append(distance(h,l))
    return [right_ret, left_ret]


def joint_distance(target_id, joint_a, joint_b):
    temp = data[get_slice(target_id)]
    ret = []
    idx_a = get_joint_slice(joint_a)
    idx_b = get_joint_slice(joint_b)
    for i in range(0, len(temp), 3):
        a = []
        b = []
        for j in range(3):
            a.append(float(temp[i+j][idx_a]))
            b.append(float(temp[i+j][idx_b]))
        ret.append(distance(a,b))
    return ret


def degree(a,b,c):
    # a = [x,y,z], b = [x,y,z], c = [x,y,z]
    a = [float(x) for x in a]
    b = [float(x) for x in b]
    c = [float(x) for x in c]
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return(int(round(np.degrees(angle))))


def knee_degree(target_id, left_or_right):
    temp = data[get_slice(target_id)]
    ret = []

    for i in range(0, len(temp), 3):
        joint = {'RKnee':[],'RHip':[],'RFoot':[]}
        if left_or_right == 'l':
            joint = {'LKnee' : [], 'LHip' : [], 'LFoot' : []}

        for joint_temp in joint.keys():
            for j in range(3): #x,y,z
                joint[joint_temp].append(
                    float(temp[i+j][get_joint_slice(joint_temp)]))
        
        if left_or_right == 'r':
            ret.append(degree(joint['RHip'], joint['RKnee'], joint['RFoot'],))
        elif left_or_right == 'l':
            ret.append(degree(joint['LHip'], joint['LKnee'], joint['LFoot']))
    return ret


def max_peak(time_series):
    std = 7
    half_std = std//2
    local_max = []
    i = half_std

    while True:
        #break point
        if i==len(time_series)-half_std:
            break

        # check the left value
        for left in range(i-half_std, i):
            if not time_series[left] < time_series[left+1]:
                break
        else:
            #check the right value
            for right in range(i, i+half_std):
                if not time_series[right] > time_series[right+1]:
                    break
            else:
                local_max.append(i)
        i+=1
    return local_max

def min_peak(time_series):
    std = 7
    half_std = std//2
    local_min = []
    i = half_std

    while True:
        #break point
        if i==len(time_series)-half_std:
            break

        # check the left value
        for left in range(i-half_std, i):
            if time_series[left] < time_series[left+1]:
                break
        else:
            #check the right value
            for right in range(i, i+half_std):
                if time_series[right] > time_series[right+1]:
                    break
            else:
                local_min.append(i)
        i+=1
    return local_min


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def DTW(t,c): ## 비교할 2개의 data
    mat = [[0]*len(c) for _ in range(len(t))]
    mat = np.array(mat)
    #mat setting
    size_t = len(t)
    size_c = len(c)
    for y in range(size_t):
        for x in range(size_c):
            mat[size_t-y-1][x] = np.abs(t[y]-c[x])

    for i in range(size_t-2,-1,-1):mat[i][0] += mat[i+1][0]
    for i in range(1,size_c):mat[size_t-1][i] += mat[size_t-1][i-1]

    for y in range(size_t-2, -1, -1):
        for x in range(1,size_c):
            mat[y][x] += min(mat[y+1][x-1],mat[y][x-1],mat[y+1][x])
    return mat[0][-1]


def cycle_length(frame):
    ret = []
    for i in range(2, len(frame), 2): # 2,4,6,8
        ret.append(frame[i] - frame[i-2])
    return ret


def remove_outlier(local_max):
    ## TEST :: get gait cycle
    ### STD : MAX & box plot idea
    diff_frames = cycle_length(local_max)
    q1 = np.percentile(diff_frames, 25) # 1분위수
    q2 = np.percentile(diff_frames, 50) # 2분위수
    q3 = np.percentile(diff_frames, 75) # 3분위수
    iqr = q3 - q1
    limit_min = q1 - iqr * 1.5
    limit_max = q3 + iqr * 1.5
    
    ignore_frame = []
    for i in range(0, len(diff_frames)):
        if not limit_min < diff_frames[i] < limit_max:
            ignore_frame.append([local_max[i*2], local_max[i*2+2]])
            diff_frames[i] = -1
    return ignore_frame #return outlier cycle


def is_convex_up(local_max1, local_max2, local_min1, local_min2, mid):
    return True if (local_max1 < local_min1 < mid) and (local_max2 < local_min2 < mid) else False