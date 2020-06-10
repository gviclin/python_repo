# some_file.py
import sys
import os

import logging

sys.path.insert(1, os.getcwd()+"/stravaio")

import pandas as pd
import numpy as np

import datetime
import time
from datetime import timedelta  

from critical_power import CriticalPower
from activity import Activity
from statist import Statist
from activity import Activity

def login(token):
	act = Activity(token)
	
	endDate = datetime.datetime.now() +  timedelta(hours=24) 
	startDate = endDate - timedelta(days=31)
	#startDate = endDate - timedelta(days=31*12*15)
	act.retreive_strava_activities(startDate, endDate)	

	athlete = act.getAthlete()
	
	return athlete

def getStatByMonth(list):	
	# create logger
	logger = logging.getLogger('')
	logger.setLevel(logging.DEBUG)
	
	stat = Statist(logger)

	athlete_id = 134706
	
	return stat.Stat_dist_by_month(athlete_id,list)	
	
	#wait = input("PRESS ENTER TO CONTINUE.")
	
def getStatAnnual(list,listObjective):	
	# create logger
	logger = logging.getLogger('')
	logger.setLevel(logging.DEBUG)
	
	stat = Statist(logger)
	
	athlete_id = 134706
	
	return stat.Stat_dist_annual(athlete_id,list,listObjective)
	#return stat.Stat_dist_annual(athlete_id,list,[1400,1600])
	#stat.Stat_dist_annual(athlete["id"],["Run"],[600,700])	
	
	#wait = input("PRESS ENTER TO CONTINUE.")
	

if __name__ == "__main__":
	run()



