# -*- coding: UTF-8 -*-
import matplotlib
import matplotlib.pyplot as plt
import pandas
import datetime
import numpy as np

print 'pandas.__version__ is ', pandas.__version__
print 'matplotlib.__version__ is ', matplotlib.__version__

dStart = datetime.datetime(2011, 5, 1)  # 1 May
dEnd = datetime.datetime(2011, 7, 1)  # 1 July

dateIndex = pandas.date_range(start=dStart, end=dEnd, freq='D')
print "1 May to 1 July 2011", dateIndex

testSeries = pandas.Series(data=np.random.randn(len(dateIndex)), index=dateIndex)

ax = plt.figure(figsize=(7, 4), dpi=300).add_subplot(111)
testSeries.plot(ax=ax, style='v-', label='first line')

# using MatPlotLib date time locators and formatters doesn't work with new
# pandas datetime index
ax.xaxis.set_minor_locator(matplotlib.dates.WeekdayLocator(byweekday=(1), interval=1))
ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d\n%a'))
ax.xaxis.grid(True, which="minor")
ax.xaxis.grid(False, which="major")
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('\n\n\n%b%Y'))
plt.show()

# set the major xticks and labels through pandas
ax2 = plt.figure(figsize=(7, 4), dpi=300).add_subplot(111)
xticks = pandas.date_range(start=dStart, end=dEnd, freq='W-Tue')
print "xticks: ", xticks
testSeries.plot(ax=ax2, style='-v', label='second line',
                xticks=xticks.to_pydatetime())
ax2.set_xticklabels([x.strftime('%a\n%d\n%h\n%Y') for x in xticks]);
# set the text of the first few minor ticks created by pandas.plot
# ax2.set_xticklabels(['a','b','c','d','e'], minor=True)
# remove the minor xtick labels set by pandas.plot 
ax2.set_xticklabels([], minor=True)
# turn the minor ticks created by pandas.plot off 
# plt.minorticks_off()
plt.show()
print testSeries['6/4/2011':'6/7/2011']