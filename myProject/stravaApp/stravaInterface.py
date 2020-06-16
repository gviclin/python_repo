# some_file.py
import sys
import os

import logging

from loguru import logger

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
	
def logoff(access_token):	
	stravaio.deauthorize(access_token)
	
def getAthlete(access_token):
	access = stravaio.StravaIO(access_token=access_token)
	
	'''
	endDate = datetime.datetime.now() +  timedelta(hours=24) 
	startDate = endDate - timedelta(days=31)
	#startDate = endDate - timedelta(days=31*12*15)
	act.retreive_strava_activities(startDate, endDate)	'''
		

	athlete = access.get_logged_in_athlete()
	
	if athlete is not None:	
		athlete = athlete.to_dict()
			
		logger.debug("athlete : id " + str(athlete["id"]) + ", " + athlete["firstname"] + " " + athlete["lastname"] + " from " + athlete["city"] + ", " + str(athlete["weight"]) + "kg")
	else:
		logger.debug(f"Error in calling Strava API for acces token <" + access_token + ">")	
		athlete = None
		
	return athlete
	

def getStatByMonth(id, list):	
	# create logger
	logger = logging.getLogger('')
	logger.setLevel(logging.DEBUG)
	
	stat = Statist(logger)

	#athlete_id = 134706
	
	return stat.Stat_dist_by_month(id,list)	
	
	#wait = input("PRESS ENTER TO CONTINUE.")
	
def getStatAnnual(id, list,listObjective):	
	# create logger
	logger = logging.getLogger('')
	logger.setLevel(logging.DEBUG)
	
	stat = Statist(logger)
	
	#athlete_id = 134706
	
	return stat.Stat_dist_annual(id,list,listObjective)
	
	#wait = input("PRESS ENTER TO CONTINUE.")
	

if __name__ == "__main__":
	run()



