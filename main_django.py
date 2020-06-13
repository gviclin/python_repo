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
from activity import Activity
from activity import actDeauthorize

from stravaio import StravaIO

def logoff(acces_token):
	actDeauthorize(acces_token)


def login(user_token):

	'''# Show python path
	for p in sys.path:
		print(" - " + p)
	return'''
	
	act = Activity(user_token)
	
	return act.ACCESS_TOKEN
	
def getAthlete(access_token):
	access = StravaIO(access_token=access_token)
	
	'''
	endDate = datetime.datetime.now() +  timedelta(hours=24) 
	startDate = endDate - timedelta(days=31)
	#startDate = endDate - timedelta(days=31*12*15)
	act.retreive_strava_activities(startDate, endDate)	'''

	athlete = access.get_logged_in_athlete()
	return athlete.to_dict()
	

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



