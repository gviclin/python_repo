from stravaio import strava_oauth2
from stravaio import StravaIO
from stravaio import dir_stravadata
from stravaio import convert_datetime_to_iso8601

import os
import json
import glob
from pathlib import Path
import pandas as pd
import numpy as np
import cv2

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tick

import seaborn as sns
#from scipy import signalsignal
import datetime
import time

import pprint 

class Activity():
	
	def __init__(self):
		# Public identifier for apps
		self.STRAVA_CLIENT_ID = 9402
		
		# Secret known only to the application and the authorization server
		self.STRAVA_CLIENT_SECRET = "7960741d3c1563506e073c364e71473c5da1405c"

		access_token = self.read_file_token()

		self.client = StravaIO(access_token=access_token)
		print (self.client)		
		
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

				
	def read_file_token(self):
		try:
			myFile = open('access_token','r')
			
			token = myFile.read()
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
			
			token = myFile.read()
			
		except:
			print("Unexpected error:", sys.exc_info()[0])

		finally:
			myFile.close
			
		myFile.close
		#print ('STRAVA_ACCESS_TOKEN : ' + str (token))
		return token
		

	def get_activities(self):
		"""Get activitiesfrom activity ID

		Returns
		-------
		activity: dataframe object
		"""
		
		# Get list of athletes activities since a given date (after) given in a human friendly format.
		# Kudos to [Maya: Datetimes for Humans(TM)](https://github.com/kennethreitz/maya)
		# Returns a list of [Strava SummaryActivity](https://developers.strava.com/docs/reference/#api-models-SummaryActivity) objects
		list_activities = self.client.get_logged_in_athlete_activities(after='last week',page=0,per_page =100 )
		
		pp = pprint.PrettyPrinter(indent=4)
		#pp.pprint(list_activities[0])

		print("list_activities : ", len(list_activities), " elements")
		
		strava_dir = dir_stravadata()
		athlete_id = self.athlete.id
		activities_dir = os.path.join(strava_dir, f"summary_activities_{athlete_id}")
		if not os.path.exists(activities_dir):
			os.mkdir(activities_dir)
		
		streams = []
		
		# Obvious use - store all activities locally
		for a in list_activities:
			
			#store activity
			print(a.dump())
			_dict = a.to_dict()
			_dict = convert_datetime_to_iso8601(_dict)

			f_name = f"summary_activity_{a.id}.json"
			with open(os.path.join(activities_dir, f_name), 'w') as fp:
				json.dump(_dict, fp)
			
			#store stream if not exist yet
			if not self.isStreamStored(a.id):
				streams = self.client.get_activity_streams(a.id, self.athlete.id, False) #local = False to retreive data from Strava
				streams.store_locally()
				streams = pd.DataFrame(streams.to_dict())
			else:
				dir_streams = os.path.join(dir_stravadata(), f"streams_{self.athlete.id}")
				f_name = f"streams_{a.id,}.parquet"
				f_path = os.path.join(dir_streams, f_name)
				if f_path in glob.glob(f_path):
					streams = pd.read_parquet(f_path)
			
			print("stream id : ",a.id)


	def isStreamStored(self,activity_id):
		strava_dir = dir_stravadata()
		streams_dir = os.path.join(strava_dir, f"streams_{self.athlete.id}")
		streams_dir = os.path.join(streams_dir, f"streams_{activity_id}.parquet")
		print(streams_dir)
		if os.path.isfile(streams_dir):
			return True
		else:
			return False

		


