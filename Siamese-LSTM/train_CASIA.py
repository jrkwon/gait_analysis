"""
history:
    2021-05-08: fix for Keras 2.0
"""

from time import time
import pandas as pd
import numpy as np

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

import tensorflow as tf

from tensorflow.python.keras.models import Model, Sequential
from tensorflow.python.keras.layers import Input, LSTM, GRU, Conv1D, Conv2D, GlobalMaxPool1D, Dense, Dropout

from util import ManDist

# File paths
TRAIN_CSV = './data/preprocessing_siamese127.csv'  # CASIA-A
#TRAIN_CSV = './data/mars_merge.csv' # MARS dataset

# Load training set
train_df = pd.read_csv(TRAIN_CSV)


X = train_df[['x_RFoot_1', 'x_LFoot_1', 'x_RKnee_1', 'x_LKnee_1', 'x_LHip_1', 'x_RHip_1', 'y_RFoot_1', 'y_LFoot_1', 'y_RKnee_1', 'y_LKnee_1', 'y_LHip_1', 'y_RHip_1', 'z_RFoot_1', 'z_LFoot_1', 'z_RKnee_1', 'z_LKnee_1', 'z_LHip_1', 'z_RHip_1','x_RFoot_2', 'x_LFoot_2', 'x_RKnee_2', 'x_LKnee_2', 'x_LHip_2', 'x_RHip_2', 'y_RFoot_2', 'y_LFoot_2', 'y_RKnee_2', 'y_LKnee_2', 'y_LHip_2', 'y_RHip_2', 'z_RFoot_2', 'z_LFoot_2', 'z_RKnee_2', 'z_LKnee_2', 'z_LHip_2', 'z_RHip_2']]
X = X.astype('float32')
scaler = MinMaxScaler(feature_range=(0,1))
X = scaler.fit_transform(X)

# Y = [1 if a[:-2] == b[:-2] else 0 for a,b in zip(train_df['id_1'], train_df['id_2'])]
Y = [1 if a[:-4] == b[:-4] else 0 for a,b in zip(train_df['id_1'], train_df['id_2'])]


#train, validation
X_train = {'left':[],'right':[]}
X_validation = {'left':[],'right':[]}
Y_train = []
Y_validation = []


for id_1, id_2, data_x, data_y in zip(train_df['id_1'], train_df['id_2'], X, Y):
    if id_1.split('_')[1] == '1' or id_2.split('_')[1] == '1':
        X_validation['left'].append(data_x[:18])
        X_validation['right'].append(data_x[18:])
        Y_validation.append(data_y)
    else:
        X_train['left'].append(data_x[:18])
        X_train['right'].append(data_x[18:])
        Y_train.append(data_y)

# Make sure everything is ok
assert len(X_train['left']) == len(Y_train)

# Model variables
gpus = 1
# batch_size = 512 * gpus
batch_size = 1024
n_epoch = 10
n_hidden = 40

max_timestamp = 127 ##
feature_cnt = 18 ##

x_validation_left = np.array(X_validation['left'])
x_validation_right = np.array(X_validation['right'])
x_train_left = np.array(X_train['left'])
x_train_right = np.array(X_train['right'])

x_validation_left = x_validation_left.reshape(x_validation_left.shape[0]//max_timestamp, max_timestamp, feature_cnt)
x_validation_right = x_validation_right.reshape(x_validation_right.shape[0]//max_timestamp, max_timestamp, feature_cnt)
x_train_left = x_train_left.reshape(x_train_left.shape[0]//max_timestamp, max_timestamp, feature_cnt)
x_train_right = x_train_right.reshape(x_train_right.shape[0]//max_timestamp, max_timestamp, feature_cnt)

# Define the shared model
x = Sequential()
# LSTM
x.add(LSTM(n_hidden, input_shape=(max_timestamp,feature_cnt)))
shared_model = x

# The visible layer
left_input = Input(shape=(max_timestamp,feature_cnt), dtype='float32')
right_input = Input(shape=(max_timestamp,feature_cnt), dtype='float32')

# Pack it all up into a Manhattan Distance model
malstm_distance = ManDist()([shared_model(left_input), shared_model(right_input)])
model = Model(inputs=[left_input, right_input], outputs=[malstm_distance])

model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(), metrics=['accuracy'])
model.summary()
shared_model.summary()


# Start trainings
training_start_time = time()
malstm_trained = model.fit([x_train_left, x_train_right], np.array(Y_train[::max_timestamp]),
                           batch_size=batch_size, epochs=n_epoch,
                           validation_data=([x_validation_left, x_validation_right], np.array(Y_validation[::max_timestamp])))
training_end_time = time()
print("Training time finished.\n%d epochs in %12.2f" % (n_epoch, training_end_time - training_start_time))

model.save('./data/SiameseLSTM2021-05-08-casia-a.h5')

# Plot accuracy
plt.figure()
plt.subplot(211)
plt.plot(malstm_trained.history['accuracy'])
plt.plot(malstm_trained.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='lower right')
#plt.savefig('./data/history-graph-accuracy.png')
#plt.savefig('./data/history-graph-accuracy.pdf')

# Plot loss
plt.subplot(212)
#plt.figure()
plt.plot(malstm_trained.history['loss'])
plt.plot(malstm_trained.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper right')

plt.tight_layout(h_pad=1.0)
#plt.savefig('./data/history-graph-loss.png')
#plt.savefig('./data/history-graph-loss.pdf')

plt.savefig('./data/history-graph.png')
plt.savefig('./data/history-graph.pdf')

print(str(malstm_trained.history['val_accuracy'][-1])[:6] +
      "(max: " + str(max(malstm_trained.history['val_accuracy']))[:6] + ")")
print("Done.")

