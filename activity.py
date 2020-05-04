from stravaio import strava_oauth2
from stravaio import StravaIO

import pandas as pd
import numpy as np
import cv2

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tick

import seaborn as sns
#from scipy import signalsignal
#import datetime
import time



class Activity():

	def __init__(self):
		# Public identifier for apps
		self.STRAVA_CLIENT_ID = 9402
		
		# Secret known only to the application and the authorization server
		self.STRAVA_CLIENT_SECRET = "7960741d3c1563506e073c364e71473c5da1405c"
	
		try:
			myFile = open('access_token','r')
			
		except IOError:

			# get the strava accept
			token  = strava_oauth2(client_id=self.STRAVA_CLIENT_ID, client_secret=self.STRAVA_CLIENT_SECRET)	

			self.expire_date = time.ctime(int(token["expires_at"]))
			print ("Access to strava ok. Access expires at :", self.expire_date)
			#print ("token :",  str(token))
						
			myFile = open('access_token','w')
			myFile.write(token["access_token"])
			myFile.close()
			myFile = open('access_token','r')
			
		
		except:
			print("Unexpected error:", sys.exc_info()[0])

		finally:
			myFile.close

		access_token = myFile.read()
		# print ('STRAVA_ACCESS_TOKEN : ' + str (access_token))

		self.client = StravaIO(access_token=access_token)
		#print ("client :" + str(type(client)))
		
		
		# Get logged in athlete (e.g. the owner of the token)
		# Returns a stravaio.Athlete object that wraps the
		# [Strava DetailedAthlete](https://developers.strava.com/docs/reference/#api-models-DetailedAthlete)
		# with few added data-handling methods
		self.athlete = self.client.get_logged_in_athlete()
		#print ("athlete :", str(self.athlete))

		# Dump athlete into a JSON friendly dict (e.g. all datetimes are converted into iso8601)
		athlete_dict = self.athlete.to_dict()

		# Store athlete infor as a JSON locally (~/.stravadata/athlete_<id>.json)
		# i.e. C:\Users\gaelv\.stravadata\athlete_134706.json
		self.athlete.store_locally()

		# Get locally stored athletes (returns a generator of dicts)
		#local_athletes = client.local_athletes()
				
		

	def get_activities(self):
		"""Get activitiesfrom activity ID

		Returns
		-------
		activity: dataframe ojbect
		"""
		
		# Get list of athletes activities since a given date (after) given in a human friendly format.
		# Kudos to [Maya: Datetimes for Humans(TM)](https://github.com/kennethreitz/maya)
		# Returns a list of [Strava SummaryActivity](https://developers.strava.com/docs/reference/#api-models-SummaryActivity) objects
		list_activities = self.client.get_logged_in_athlete_activities(after='last month')

		# Obvious use - store all activities locally
		for a in list_activities:
			activity = self.client.get_activity_by_id(a.id)
			#activity.store_locally()
			 #dict1 = activity.to_dict()
			#print(" - sum up", activity)
			#print("   - type :", dict1["Activity"])
			#"distance : ",  dict1["distance"]/1000)
		




