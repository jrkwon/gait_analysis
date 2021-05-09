# import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import numpy as np
import csv
#import mplcursors


data = []
with open('./merge_CASIA_12.csv', 'r', encoding = 'utf-8') as f:
    rdr = csv.reader(f)
    for i, line in enumerate(rdr):
        if i==0:
            continue
        # if int(line[0]) > 1000:
        #     break
        # if line[0].split('_')[1] == '45':
        #     continue
        line[0] = line[0].split('_')[0][:2]
        temp = [int(float(x)) for x in line]
        data.append(temp)
feature = []
labels = []
for row in data:
    feature.append(row[1:])
    labels.append(row[0])
model = TSNE(learning_rate=200, n_iter=700, verbose=2, perplexity=20)
transformed = model.fit_transform(feature)
xs = transformed[:,0]
ys = transformed[:,1]


markers = ['o','X', '^', '<', '>', '8', '*']
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
duet = []
for m in markers:
    for c in colors:
        duet.append([m,c])
symbols = list(set(labels))
draw = {}
for i, symbol in enumerate(symbols):
    draw[symbol] = duet[i]

for i in range(len(xs)):
    plt.scatter(xs[i],ys[i],c=draw[labels[i]][1], marker=draw[labels[i]][0])
#plt.scatter(xs,ys,c=labels, cmap='viridis')

plt.grid(True)

plt.show()
