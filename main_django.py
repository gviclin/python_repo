# some_file.py
import sys
import os

import logging


import pandas as pd
import numpy as np

import datetime
import time
from datetime import timedelta  

from critical_power import CriticalPower
from activity import Activity
from statist import Statist

def getStatByMonth():	
	# create logger
	logger = logging.getLogger('')
	logger.setLevel(logging.DEBUG)
	
	# create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	# create formatter
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# add formatter to ch
	ch.setFormatter(formatter)

	# add ch to logger
	logger.addHandler(ch)

	'''
	#get an instance of CriticalPower
	cp = CriticalPower()
	#HT  : 3330576768 
	#CAP : 3136818310
	# Get critical power matrix
	df = cp.get_cp_list_by_id(3412908429)
	#cp.show_plot(df)'''
	
	athlete_id = 134706

	stat = Statist(logger)
	
	return stat.Stat_dist_by_month(athlete_id,["Run"])
	#stat.Stat_dist_annual(athlete_id,["Run"],[1400,1600])
	#stat.Stat_dist_annual(athlete["id"],["Run"],[600,700])	
	
	#wait = input("PRESS ENTER TO CONTINUE.")
	


if __name__ == "__main__":
	run()



