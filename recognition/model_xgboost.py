from xgboost import XGBClassifier
from catboost import CatBoostClassifier, CatBoost, Pool
from xgboost import plot_importance

from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, f1_score
# for scikit-learn 0.22
#from sklearn.grid_search import GridSearchCV # this is for 0.17 version
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
import itertools
# from sklearn.cross_validation import train_test_split
import random
import pandas as pd
import numpy as np
import json

# .. casia dataset
data = pd.read_csv('./merge_CASIA_12.csv')
data['id'] = [n[:4] for n in data['id']]
# .. mars dataset
#data = pd.read_csv('./feature0719-mars.csv')
#data['id'] = data['target_id']

# col = set(data.columns) - set(['upper_body','right_lower_leg','right_upper_leg','left_lower_leg','left_upper_leg'])
col = set(data.columns) - set(['target_id', 'upper_body','right_lower_leg','right_upper_leg','left_lower_leg','left_upper_leg'])
col = list(col)
data = data[col]

acc = []
f1_macro = []
f1_weight = []

# 100 times testing!
for num in range(100):
    #split train, test
    test_idx = []
    for target_id in set(data['id']):
        random.seed(2018+num)
        idx = [i for i, val in enumerate(data['id']==target_id) if val==True]
        test_idx += random.sample(idx, len(idx)//4)
    test  = data.loc[test_idx]
    train = data.loc[set(range(data.shape[0])).difference(test_idx)]


    id_list = sorted(list(set(train['id'])))
    train_y = [id_list.index(val) for val in train['id']]
    # train_y = [((int(str(val)[:2])*2) + (1 if str(val)[2:4]=='45' else 0)) for val in train['id']]
    train_x = train[[n for n in train.columns if n!='id']]

    # test_y = test['id']
    # test_y = [((int(str(val)[:2])*2) + (1 if str(val)[2:4]=='45' else 0)) for val in test['id']]
    test_y = [id_list.index(val) for val in test['id']]
    test_x = test[[n for n in test.columns if n!='id']]


    ####XGBOOST
    model = XGBClassifier(booster = 'gbtree', n_estimators=300,max_depth = 3)
    model.fit(train_x,train_y)
    pre = model.predict(test_x)

    ###CATBOOST
    # model = CatBoostClassifier(custom_loss=['Accuracy'],
    #     random_seed=42,
    #     iterations=200,
    #     loss_function='MultiClass')
    # model.fit(train_x, train_y)
    # pre = model.predict(test_x)
    # pre = [int(val) for val in pre]


    cnf_matrix = confusion_matrix(test_y, pre)
    acc.append(sum([cnf_matrix[i,i] for i in range(len(cnf_matrix))]) / len(test_y))
    f1_macro.append(f1_score(test_y,pre,average='macro'))
    f1_weight.append(f1_score(test_y,pre,average='weighted'))
    print(num, acc[num], f1_macro[num], f1_weight[num])
    # print(auc(model, train_x, test_x))

print('acc\n', min(acc), max(acc), np.mean(acc), np.median(acc), np.std(acc))
print('f1\n', min(f1_macro), max(f1_macro), np.mean(f1_macro), np.median(f1_macro), np.std(f1_macro))
print('f1\n', min(f1_weight), max(f1_weight), np.mean(f1_weight), np.median(f1_weight), np.std(f1_weight))


# label = {}
# cnt = 0
# for i in range(20):
#     for angle in ['00','45']:
#         label[cnt] = str(i)+angle
#         cnt += 1

# pre = [label[int(i)].zfill(4) for i in pre]

# cnt = 0 ##answer
# for a,b in zip(test_y, pre):
#     if a==b:
#         cnt += 1
# print('ACC: ', cnt/len(test_y))


# ###
# plt.barh(model.feature_names_, model.feature_importances_, align='center', height=0.5)
# plt.yticks(model.feature_names_)
# plt.show()

# # true = 0
# # for i in range(len(cnf_matrix)):
# #     true += cnf_matrix[i,i]
# # false = len(test_y) - true
# # print(num, '\tacc: ', true / len(test_y))

# # plot_importance(model)
# # plt.show()
