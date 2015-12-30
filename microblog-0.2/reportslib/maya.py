import random

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from mpl_toolkits.mplot3d import Axes3D

from db import dbread
import json

list=[]
days = { '2015-12-01','2015-12-02','2015-12-03','2015-12-04','2015-12-05', '2015-12-06'}
members = {'mac','guor','tanggd','gengyf','wanglj','songyq','zhangjy','zhangjy','liy'}
db = dbread()
jsonStr = db.read(days)
list = json.loads(jsonStr)
print list

fp = open("db-maya.json")
jsonStr = fp.read()
fp.close()
list = json.loads(jsonStr) # json encode to object
# print list

mpl.rcParams['font.size'] = 10

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

xs = [1,2,3,4,5,6,7,8] # xs is member
#print xs
zs = [1,2,3,4,5,6]  # zs is days
#print zs
for z in zs:
    ys=[]
    for man in list[z-1]['team']:
         ys.append(man['status']['resolve']) # resolved bugs'count per members
    print ys
    color =plt.cm.Set2(random.choice(xrange(plt.cm.Set2.N)))
    ax.bar(xs, ys, zs=z, zdir='y', color=color, alpha=0.8)
    ax.set_xticklabels(['mac','guor','tanggd','gengyf','wanglj','songyq','zhangjy','zhangjy','liy'],rotation=15)

ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xs))
ax.set_xticks([1,2,3,4,5,6,7,8])
# ax.yaxis.set_minor_locator(mpl.dates.WeekdayLocator(byweekday=(1),interval=1))
# ax.yaxis.set_minor_formatter(mpl.dates.DateFormatter('%d\n%a'))
# ax.yaxis.grid(True, which="minor")
# ax.yaxis.grid(False, which="major")
# ax.yaxis.set_major_formatter(mpl.dates.DateFormatter('\n\n\n%b%Y'))
ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ys))

ax.zaxis.set_major_locator(mpl.ticker.FixedLocator(zs))
ax.set_yticklabels(['12-01','12-02','12-03','12-04','12-05', '12-06'],rotation=-15)

ax.set_xlabel('member')
ax.set_ylabel('day')
ax.set_zlabel('resolved Bugs')

plt.show()