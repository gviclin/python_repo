import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tick
import seaborn as sns
import datetime
import time

from critical_power import CriticalPower

def getDuration(x):
	if x < 60:
		return time.strftime("%S", time.gmtime(x)) + " sec"
	elif x < 3600:
		return time.strftime("%M:%S", time.gmtime(x)) + " min"
	else:
		return time.strftime("%H:%M:%S", time.gmtime(x))

class SnaptoCursor:
    """
    Like Cursor but the crosshair snaps to the nearest x, y point.
    For simplicity, this assumes that *x* is sorted.
    """

    def __init__(self, ax, x, y, windowssize):
        self.ax = ax
        self.lx = ax.axhline(color='k', linestyle=":")  # the horiz line
        self.ly = ax.axvline(color='k', linestyle=":")  # the vert line
        self.x = x
        self.y = y
        self.windowssize = windowssize
        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)
    
    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata

        indx = min(np.searchsorted(self.x, x), len(self.x) - 1)
        x = self.x[indx]
        y = self.y[indx]
        #print("x :", x, y)
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)
        #strx = time.strftime("%H:%M:%S", time.gmtime(x))
        self.txt.set_text('%1.0f watts during %s' % (y, getDuration(x)))

        #retreive axis view limits
        xmin = ax.get_xlim()[0]
        xmax = ax.get_xlim()[1]
        ymin = ax.get_ylim()[0]
        ymax = ax.get_ylim()[1]

        #print("Axes.get_xlim :", ax.get_xlim()[0], ax.get_xlim()[1])
        #print('x=%1.2f, y=%1.2f' % (x, y))

        # set the position of the text
        self.txt.set_x(((x-xmin) / (xmax-xmin)) + 10 / self.windowssize[0])
        self.txt.set_y(((y-ymin) / (ymax-ymin)) + 10 / self.windowssize[1])

        self.ax.figure.canvas.draw()


#get an instance of CriticalPower
cp = CriticalPower()

#HT  : 3330576768
#CAP : 3136818310
# Get critical power matrix
df = cp.get_cp_list_by_id(3330576768)

print("result :", str(df))

if df is not None:
	'''
	plt.plot(df["duration"], df["mean_watts"], 'x-')
	# gcf : get current figure
	plt.gcf().autofmt_xdate()
	myFmt = mdates.DateFormatter('%H:%M:%S')
	#Get the current Axes
	plt.gca().xaxis.set_major_formatter(myFmt)
	#plt.gca().set_xscale('log')
	plt.grid(True)
	plt.show()
	'''

	fig, ax = plt.subplots()
	ax.set_title('Critical power')
	ax.plot(df["isec"], df["mean_watts"], 'x-')


	def to_date(x, pos):
		str = time.strftime("%H:%M:%S", time.gmtime(x))
		#print("to_date", x, str)
		return str


	fig.autofmt_xdate()

	# strx = time.strftime("%H:%M:%S", time.gmtime(x))
	#myFmt = mdates.DateFormatter('%H:%M:%S')
	myFmt = tick.FuncFormatter(to_date)
	ax.xaxis.set_major_formatter(myFmt)
	#ax.set_xscale('log')


	plt.grid(True)
	cursor = SnaptoCursor(
		ax,
		df["isec"],
		df["mean_watts"],
		fig.get_size_inches()*fig.dpi) # size in pixels
		
	fig.canvas.mpl_connect('motion_notify_event', cursor.mouse_move)

	plt.show()




