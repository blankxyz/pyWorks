import random

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from mpl_toolkits.mplot3d import Axes3D

mpl.rcParams['font.size'] = 10

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for z in [2, 4, 6, 8, 10, 12]:  # z is days
    xs = xrange(0, 6)  # 6 member
    ys = [500, 100, 200, 300, 400, 200]  # resolved bugs'count per members

    color = plt.cm.Set2(random.choice(xrange(plt.cm.Set2.N)))
    ax.bar(xs, ys, zs=z, zdir='y', color=color, alpha=0.8)

ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xs))
ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ys))

ax.set_xlabel('member')
ax.set_ylabel('day')
ax.set_zlabel('resolved Bugs')

mpl.rcParams['font.size'] = 10

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for z in [2, 4, 6, 8, 10, 12]:  # z is days
    xs = xrange(0, 6)  # 6 member
    ys = [500, 100, 200, 300, 400, 200]  # resolved bugs'count per members

    color = plt.cm.Set2(random.choice(xrange(plt.cm.Set2.N)))
    ax.bar(xs, ys, zs=z, zdir='y', color=color, alpha=0.8)

ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xs))
ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ys))

ax.set_xlabel('member')
ax.set_ylabel('day')
ax.set_zlabel('resolved Bugs')

plt.show()

[2, 0, 0, 0, 0, 2, 3, 0]
[0, 0, 0, 0, 0, 0, 5, 0]
[0, 0, 0, 0, 9, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0]
[5, 0, 0, 0, 0, 0, 0, 0]