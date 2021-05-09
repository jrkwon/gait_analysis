######
## gait feature extraction


# 2, 4, 60, 100, 100, 104, 142, 158, 198, 202(front),
# 316, 322, 378, 386, 426, 430, 432, 500, 610, 636, 646,
# 650,670, 686, 762(front), 776, 792, 824, 868, 904, 916, 918
# 992, 1016, 1026, 1112(end), 1158(mid), 1182, 1270, 1318,
# 1372(front), 1480
import re
import sys
import matplotlib.pylab as plt
from data_utils import *
from scipy.interpolate import CubicSpline

smoothing = 12
interpoints = 4

def inicialize():
    global RDegree, LDegree, head_rfoot, head_lfoot, dis, hip_thorax_dist, right_lower_leg_dist, right_upper_leg_dist, left_lower_leg_dist, left_upper_leg_dist, inter_dis

    ## knee angle
    RDegree = knee_degree(target_id, 'r')
    LDegree = knee_degree(target_id, 'l')

    ## head <-> foot distance
    head_rfoot, head_lfoot = head_foot_distances(target_id)

    ## left, right foot distance
    dis = joint_distance(target_id, "LFoot", "RFoot")
    #dis = dis[0:20]
    # inter_dis = dis
    inter_dis = list(data_interpolation(dis, interpoints))  #  n points will be inserted between two 3d points.
    inter_dis = smooth(inter_dis, smoothing)             #  smooth 1..xx (lower is smoother)
    plt.plot([i*4 for i in range(len(dis))], dis, 'b.-', range(len(inter_dis)), inter_dis,'r-')
    plt.show()


    ## hip, thorax distance
    hip_thorax_dist = list(np.add(joint_distance(target_id, "Hip", "Spine"),joint_distance(target_id, "Spine", "Thorax")))

    ## leg distance
    right_lower_leg_dist = joint_distance(target_id, 'RFoot', 'RKnee')
    right_upper_leg_dist = joint_distance(target_id, 'RKnee', 'RHip')
    left_lower_leg_dist = joint_distance(target_id, 'LFoot', 'LKnee')
    left_upper_leg_dist = joint_distance(target_id, 'LKnee', 'LHip')
    return None


def setting_local_max():
    global local_max, max_val
    local_max = max_peak(inter_dis) #frame num
    local_max = [f//(len(inter_dis)//len(dis)) for f in local_max]
    max_val = [dis[frameNum] for frameNum in local_max] #value
    return None

def setting_local_min():
    global local_min, min_val
    local_min = min_peak(inter_dis)
    local_min = [f//(len(inter_dis)//len(dis)) for f in local_min]
    if len(local_min) > 0 and len(local_max) > 0 and local_min[0] < local_max[0]:
        local_min = local_min[1:]

    min_val = [dis[frameNum] for frameNum in local_min]
    return None

def setting_local_val():
    setting_local_max()
    setting_local_min()
    return None


def distance_cost_plot(distances):
    im = plt.imshow(distances, interpolation='nearest', cmap='Reds')
    plt.gca().invert_yaxis()
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid()
    plt.colorbar()
    plt.show()
    return None

#read_data('../output/merge_CASIA.csv') #save global 'data' value
#read_data('../output/fyc-00_1-001.mp4.csv') #save global 'data' value
read_data('../output/hy-00_1-001.mp4.csv')

# target_ids = [int(x) for x in get_id_list() if x != 'id']
target_ids = [x for x in get_id_list() if x != 'id']
target_ids.sort()

ids = sorted(list(set([re.sub('[0-9]','',ids)[:-1] for ids in target_ids])))
d = {}
for i, key in enumerate(ids):
    d[key] = i

featureset = []
for target_id in target_ids:
    if '90' in target_id: ## 90 degree data ignored?
       continue
    print('id: ', target_id, '')
    csv_save_id = str(d[re.sub('[^a-z]','',target_id)]).zfill(2) + str(target_id[-4:])
    ## degree, head<->foot distance, foot<->foot distance
    inicialize()
    ## setting local value
    setting_local_val()

    ## gait cycle preprocessing
    cycle_index = []
    index = 2
    if len(local_max) < 3 and len(local_min) < 3:
        print("no cycle ", target_id)
        continue
    while index < len(local_max):
        ## indexing
        start_max_frame = local_max[index-2]
        end_max_frame = local_max[index]
        mid_max_frame = (start_max_frame + end_max_frame)//2

        if index-1 > len(local_min):
            break
        start_min_frame = local_min[index-2]
        try:
            end_min_frame = local_min[index]
        except IndexError as e:
            end_min_frame = len(dis)-1
        mid_min_frame = (start_min_frame + end_min_frame)//2

        ##head <-> lfoot
        condition1 = is_convex_up(head_lfoot[start_max_frame], head_lfoot[end_max_frame], head_lfoot[start_min_frame], head_lfoot[end_min_frame], head_lfoot[mid_max_frame])
        condition2 = is_convex_up(head_lfoot[start_max_frame], head_lfoot[end_max_frame], head_lfoot[start_min_frame], head_lfoot[end_min_frame], head_lfoot[mid_min_frame])
        if condition1 or condition2:
            cycle_index.append(index-2)
            cycle_index.append(index)
            index += 2
        else: #leg
            index += 1

    temp_index = []
    for i in range(1, len(cycle_index)-1, 2):
        if cycle_index[i] == cycle_index[i+1]:
            temp_index.append(i)
            temp_index.append(i+1)
    for i in temp_index[::-1]:
        cycle_index.pop(i)

    ## delete right foot front...
    ignore_frame = cycle_index[1:-1]

    val_list = [dis, RDegree, LDegree, head_lfoot, head_rfoot,
                hip_thorax_dist, right_lower_leg_dist, right_upper_leg_dist,
                left_lower_leg_dist, left_upper_leg_dist]
    for i in range(len(ignore_frame)-1, 0, -2):
        for val in val_list:
            del val[local_max[ignore_frame[i-1]]:local_max[ignore_frame[i]]]

##########################################################################
    ### remove outlier
    pro_outlier = False
    if pro_outlier:
        ignore_frame = remove_outlier(max_peak(dis))
        print('outlier remove %d cycle' % len(ignore_frame))
        for start, end in ignore_frame[::-1]:
            del dis[start:end]
            del RDegree[start:end]
            del LDegree[start:end]
            del head_rfoot[start:end]
            del head_lfoot[start:end]

    setting_local_val()

    ## DTW
    pro_dtw = False
    if pro_dtw:
        dtw_distance = [[0]*(len(local_max)//2) for _ in range(len(local_max)//2)]
        for i in range(2, len(local_max), 2):
            freq1 = dis[local_max[i-2]:local_max[i]]
            for j in range(i+2, len(local_max), 2):
                freq2 = dis[local_max[j-2]:local_max[j]]
                dtw_distance[i//2-1][j//2-1] = DTW(freq1, freq2)
                dtw_distance[j//2-1][i//2-1] = dtw_distance[i//2-1][j//2-1]
        for i in dtw_distance:
            print(i)
        distance_cost_plot(dtw_distance)
##########################################################################
    ## setting row value
    hip_index = get_joint_slice('Hip')
    rknee_index = get_joint_slice('RKnee')
    lknee_index = get_joint_slice('LKnee')
    rfoot_index = get_joint_slice('RFoot')
    lfoot_index = get_joint_slice('LFoot')
    for i in range(2, len(local_max), 2): # 1cycle을 구분하기 위한 인덱스
        ###### FEATURE #####
        first_max_frame = local_max[i-2] + 1 # initial contact, loading response
        first_min_frame = local_max[i-2] # mid stance
        second_max_frame = local_max[i-1] # terminal stance, preswing
        last_min_frame = local_max[i-1] # initial swing, mid swing
        last_max_frame = local_max[i] - 1 # terminal swing

        max_Rdegree = max(RDegree[first_max_frame:last_max_frame])
        max_Ldegree = max(LDegree[first_max_frame:last_max_frame])
        min_Rdegree = min(RDegree[first_max_frame:last_max_frame])
        min_Ldegree = min(LDegree[first_max_frame:last_max_frame])

        # body length
        upper_body = np.mean(hip_thorax_dist[first_max_frame:last_max_frame])

        # leg length
        right_lower_leg = np.mean(right_lower_leg_dist[first_max_frame:last_max_frame])
        right_upper_leg = np.mean(right_upper_leg_dist[first_max_frame:last_max_frame])
        left_lower_leg = np.mean(left_lower_leg_dist[first_max_frame:last_max_frame])
        left_upper_leg = np.mean(left_upper_leg_dist[first_max_frame:last_max_frame])

        right_lower_leg2 = round(np.mean(right_lower_leg_dist[first_max_frame:last_max_frame]) / upper_body, 2)
        right_upper_leg2 = round(np.mean(right_upper_leg_dist[first_max_frame:last_max_frame]) / upper_body, 2)
        left_lower_leg2 = round(np.mean(left_lower_leg_dist[first_max_frame:last_max_frame]) / upper_body, 2)
        left_upper_leg2 = round(np.mean(left_upper_leg_dist[first_max_frame:last_max_frame]) / upper_body, 2)

        # initial contact
        initial_contact = []
        for r in get_id_frameNum(target_id, first_max_frame):
            initial_contact.append(r)

        initial_contact_hip_extension = degree([initial_contact[x][rknee_index] for x in range(3)],
                                                [initial_contact[x][hip_index] for x in range(3)],
                                                [initial_contact[x][lknee_index] for x in range(3)])
        initial_contact_left_knee_flextion = LDegree[first_max_frame]
        initial_contact_left_leg_inclination = degree([initial_contact[x][lknee_index] for x in range(3)],
                                                [initial_contact[x][lfoot_index] for x in range(3)],
                                                [initial_contact[x][lfoot_index] for x in range(2)]+[float(initial_contact[2][lfoot_index])+10])

        # mid stance
        mid_stance_knee_flextion = LDegree[first_min_frame]

        # terminal stance, Heel strike
        terminal_stance = []
        for r in get_id_frameNum(target_id, second_max_frame):
            terminal_stance.append(r)
        terminal_stance_hip_extension = degree([terminal_stance[x][rknee_index] for x in range(3)],
                                                [terminal_stance[x][hip_index] for x in range(3)],
                                                [terminal_stance[x][lknee_index] for x in range(3)])
        terminal_stance_right_knee_flextion = RDegree[second_max_frame]
        terminal_stance_right_leg_inclination = degree([terminal_stance[x][rknee_index] for x in range(3)],
                                                [terminal_stance[x][rfoot_index] for x in range(3)],
                                                [terminal_stance[x][rfoot_index] for x in range(2)]+[float(terminal_stance[2][rfoot_index])+10])
        terminal_stance_left_leg_inclination = degree([terminal_stance[x][lknee_index] for x in range(3)],
                                                [terminal_stance[x][lfoot_index] for x in range(3)],
                                                [terminal_stance[x][lfoot_index] for x in range(2)]+[float(terminal_stance[2][lfoot_index])+10])

        # initial swing
        initial_swing_knee_flextion = RDegree[last_min_frame]

        # terminal swing, toe off
        terminal_swing = []
        for r in get_id_frameNum(target_id, last_max_frame):
            terminal_swing.append(r)
        terminal_swing_hip_extension = degree([terminal_swing[x][rknee_index] for x in range(3)],
                                                [terminal_swing[x][hip_index] for x in range(3)],
                                                [terminal_swing[x][lknee_index] for x in range(3)])
        terminal_swing_right_leg_inclination = degree([terminal_swing[x][rknee_index] for x in range(3)],
                                                [terminal_swing[x][rfoot_index] for x in range(3)],
                                                [terminal_swing[x][rfoot_index] for x in range(2)]+[float(terminal_swing[2][rfoot_index])+10])


        # period
        period = last_max_frame - first_max_frame
        RFoot_period = (last_min_frame - first_min_frame)/period
        LFoot_period = (first_min_frame - first_max_frame + last_max_frame - last_min_frame)/period

        # stride length
        left_stride = (dis[first_max_frame]+dis[last_max_frame])/2
        right_stride = dis[second_max_frame]
        main_foot = 1 if left_stride > right_stride else 0 ## 왼발잡이면 1 아니면 0
        # print(target_id, (dis[first_max_frame]+dis[last_max_frame])/2, dis[second_max_frame] )

        row = [csv_save_id,
            max_Rdegree,
            max_Ldegree,
            min_Rdegree,
            min_Ldegree,
            upper_body,
            right_lower_leg,
            right_upper_leg,
            left_lower_leg,
            left_upper_leg,
            right_lower_leg2,
            right_upper_leg2,
            left_lower_leg2,
            left_upper_leg2,
            initial_contact_hip_extension,
            initial_contact_left_knee_flextion,
            initial_contact_left_leg_inclination,
            mid_stance_knee_flextion,
            terminal_stance_hip_extension,
            terminal_stance_right_knee_flextion,
            terminal_stance_right_leg_inclination,
            terminal_stance_left_leg_inclination,
            initial_swing_knee_flextion,
            terminal_swing_hip_extension,
            terminal_swing_right_leg_inclination,
            RFoot_period,
            LFoot_period,
            period,
            left_stride,
            right_stride,
            main_foot
            ]
        featureset.append(row)

##########################################################################
    ## draw
    pro_draw = False
    if pro_draw:
        ax1 = plt.subplot(2, 1, 1)
        plt.plot(range(len(dis)), dis, 'r--', local_max, max_val, 'bo', local_min, min_val, 'go')

        for i in range(0, len(local_max), 2):
            ax1.vlines(x=local_max[i], ymin=100, ymax=400, linewidth=1, color='b')
        # for frame in local_min:
        #     ax1.vlines(x=frame, ymin=100, ymax=400, linewidth=1, color='g')
        plt.ylabel('foot distance')
        print(ax1)

        # ax2 = plt.subplot(3, 1, 2)
        # {
        #     # Rhat = smooth(RDegree, 100)
        #     # Lhat = smooth(LDegree, 100)
        #     # print(Rhat)
        #     # print(Lhat)
        #     # plt.plot(range(len(RDegree)), Rhat, 'y-', range(len(LDegree)), Lhat, 'm-')
        # }
        # plt.plot(range(len(RDegree)), RDegree, 'r-', range(len(LDegree)), LDegree, 'y-')
        # for i in range(0, len(local_max), 2):
        #     ax2.vlines(x=local_max[i], ymin=150, ymax=170, linewidth=1, color='b')
        # for frame in local_min:
        #     ax2.vlines(x=frame, ymin=150, ymax=170, linewidth=1, color='g')
        # # for frame in local_min:
        # #     ax2.vlines(x=frame, ymin=150, ymax=170, linewidth=1, color='g')
        # plt.xlabel('frame')
        # plt.ylabel('Knee degree')
        # print(ax2)

        ax3 = plt.subplot(2, 1, 2)
        plt.plot(range(len(head_lfoot)), head_lfoot, 'y--', range(len(head_rfoot)), head_rfoot, 'r--')
        for i in range(0, len(local_max), 2):
            ax3.vlines(x=local_max[i], ymin=550, ymax=800, linewidth=1, color='b')
        for frame in local_min:
            ax3.vlines(x=frame, ymin=650, ymax=800, linewidth=1, color='g')
        print(ax3)
        plt.tight_layout()
        plt.show()


pro_feature_save = True
csv_header = ['id',
            'max_Rdegree',
            'max_Ldegree',
            'min_Rdegree',
            'min_Ldegree',
            'upper_body',
            'right_lower_leg',
            'right_upper_leg',
            'left_lower_leg',
            'left_upper_leg',
            'right_lower_leg2',
            'right_upper_leg2',
            'left_lower_leg2',
            'left_upper_leg2',
            'initial_contact_hip_extension',
            'initial_contact_left_knee_flextion',
            'initial_contact_left_leg_inclination',
            'mid_stance_knee_flextion',
            'terminal_stance_hip_extension',
            'terminal_stance_right_knee_flextion',
            'terminal_stance_right_leg_inclination',
            'terminal_stance_left_leg_inclination',
            'initial_swing_knee_flextion',
            'terminal_swing_hip_extension',
            'terminal_swing_right_leg_inclination',
            'RFoot_period',
            'LFoot_period',
            'period',
            'left_stride',
            'right_stride',
            'main_foot'
            ]
if pro_feature_save:
    with open('./merge_CASIA_' + str(smoothing) + '.csv','w', encoding='utf-8', newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(csv_header)
        for r in featureset:
            wr.writerow(r)
