import random
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from mpl_toolkits.mplot3d import Axes3D

mpl.rcParams['font.size'] = 10
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

n_angles = 36
n_radii = 8

# An array of radii
# Does not include radius r=0, this is to eliminate duplicate points
radii = np.linspace(0.125, 1.0, n_radii)

# An array of angles
angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)

# Repeat all angles for each radius
angles = np.repeat(angles[..., np.newaxis], n_radii, axis=1)

# Convert polar (radii, angles) coords to cartesian (x, y) coords
# (0, 0) is added here. There are no duplicate points in the (x, y) plane
xs = np.append(0, (radii * np.cos(angles)).flatten())
ys = np.append(0, (radii * np.sin(angles)).flatten())

# Pringle surface

zs = np.sin(-xs * ys)

list = []
days = {'2015-12-01', '2015-12-02', '2015-12-03', '2015-12-04', '2015-12-05', '2015-12-06'}
members = {'mac', 'guor', 'tanggd', 'gengyf', 'wanglj', 'songyq', 'zhangjy', 'zhangjy', 'liy'}

fp = open("db-maya.json")
jsonStr = fp.read()
fp.close()
list = json.loads(jsonStr)  # json encode to object

xs = range(len(members))  # xs is member
# print xs
zs = range(len(days))  # zs is days
for z in zs:
    ys = []
    for man in list[z]['team']:
        ys.append(man['status']['resolve'])  # resolved bugs'count per members
    color = plt.cm.Set2(random.choice(xrange(plt.cm.Set2.N)))
    ax.bar(xs, ys, zs=z, zdir='y', color=color, alpha=0.8)

fig = plt.figure()
ax = fig.gca(projection='3d')

ax.plot_trisurf(xs, ys, zs, cmap=cm.jet, linewidth=0.2)

plt.show()