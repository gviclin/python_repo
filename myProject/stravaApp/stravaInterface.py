# some_file.py
import sys
import os

import logging

import pandas as pd
import numpy as np

import datetime
import time
from datetime import timedelta  

import stravaio 

from statist import Statist

def login(user_token):
	# Public identifier for apps
	STRAVA_CLIENT_ID = 9402
	
	# Secret known only to the application and the authorization server
	STRAVA_CLIENT_SECRET = "7960741d3c1563506e073c364e71473c5da1405c"
	
	ACCESS_TOKEN = stravaio.get_access_token(
		port=8000,
		client_id=STRAVA_CLIENT_ID,
		client_secret=STRAVA_CLIENT_SECRET,
		user_token=user_token
	)	
	return ACCESS_TOKEN
	
def logoff(acces_token):	
	stravaio.deauthorize(access_token)
	
def getAthlete(access_token):
	access = stravaio.StravaIO(access_token=access_token)
	
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



