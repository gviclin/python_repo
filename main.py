# some_file.py
import sys
import os

import logging

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd()+"/stravaio")

#sys.path.append('./')

import pandas as pd
import numpy as np

import datetime
import time

from critical_power import CriticalPower
from activity import Activity
from statist import Statist

def run():	
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

	
	'''act = Activity()
	annee = 2020
	month=1
	startdate = datetime.datetime(annee,month, 1, 1,1,1)
	startbefore = datetime.datetime.now()
	act.retreive_strava_activities(startdate, startbefore)'''
	
	athlete_id = 134706


	stat = Statist(logger)
	#stat.Compute_the_local_db(athlete_id)
	
	
	#stat.Stat_dist_by_month(athlete_id,["Run"])
	#stat.Stat_dist_by_month(athlete_id,["Ride","VirtualRide"])
	
	#stat.Stat_dist_annual(athlete_id,["Run"])
	stat.Stat_dist_annual(athlete_id,["Ride","VirtualRide"])
	
run()



