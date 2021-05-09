from data_utils import data_interpolation,smooth
import pandas as pd

data = pd.read_csv('../output/merge_CASIA.csv')
id_list = set(data['id'])

save_data = pd.DataFrame(columns=data.columns)

for _id in sorted(list(id_list)):
    if '90' in _id:
        continue
    print(_id)
    temp = data[data['id'] == _id]
    merge_df = pd.DataFrame(columns=temp.columns)
    x_df = pd.DataFrame(columns=temp.columns)
    y_df = pd.DataFrame(columns=temp.columns)
    z_df = pd.DataFrame(columns=temp.columns)
    
    x = temp[temp['x..y..z']=='x']
    y = temp[temp['x..y..z']=='y']
    z = temp[temp['x..y..z']=='z']
    for col in x.columns[4:]:
        x_df[col] = smooth(data_interpolation(x[col],5),6)
        y_df[col] = smooth(data_interpolation(y[col],5),6)
        z_df[col] = smooth(data_interpolation(z[col],5),6)

    x_df['id'] = _id
    x_df['camera'] = 0
    x_df['frameNum'] = range(0,x_df.shape[0])
    x_df['x..y..z'] = 'x'
    y_df['id'] = _id
    y_df['camera'] = 0
    y_df['frameNum'] = range(0,y_df.shape[0])
    y_df['x..y..z'] = 'y'
    z_df['id'] = _id
    z_df['camera'] = 0
    z_df['frameNum'] = range(0,z_df.shape[0])
    z_df['x..y..z'] = 'z'

    for i in range(len(x_df)):
        save_data = save_data.append(x_df.loc[i])
        save_data = save_data.append(y_df.loc[i])
        save_data = save_data.append(z_df.loc[i])
save_data.to_csv("inter6+smooth.csv")


