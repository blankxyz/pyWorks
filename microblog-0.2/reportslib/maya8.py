# -*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, DateFormatter
autodates = AutoDateLocator()
yearsFmt = DateFormatter('%Y-%m-%d %H:%M:%S')
fig = plt.figure()
fig.autofmt_xdate()        #设置x轴时间外观
ax = fig.add_subplot(111)
ax.xaxis.set_major_locator(autodates)       #设置时间间隔
ax.xaxis.set_major_formatter(yearsFmt)      #设置时间显示格式
ax.set_xticks() #设置x轴间隔
ax.set_xlim()   #设置x轴范围

plt.show()