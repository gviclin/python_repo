from stravaio import strava_oauth2
from stravaio import StravaIO

import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import signal
#import datetime
import time


class CriticalPower():

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
				
		

	def get_cp_list_by_id(self, activity_id):
		"""Get critical power dataframe from activity ID

		Returns
		-------
		activity: dataframe ojbect
		"""
		

		# Get list of athletes activities since a given date (after) given in a human friendly format.
		# Kudos to [Maya: Datetimes for Humans(TM)](https://github.com/kennethreitz/maya)
		# Returns a list of [Strava SummaryActivity](https://developers.strava.com/docs/reference/#api-models-SummaryActivity) objects
		#list_activities = client.get_logged_in_athlete_activities(after='last week')

		# Obvious use - store all activities locally
		#for a in list_activities:
		#    activity = client.get_activity_by_id(a.id)
		 #   activity.store_locally()

		activity = self.client.get_activity_by_id(activity_id)
		print(str(activity))
		 

			# Returns a stravaio.Streams object that wraps the 
		# [Strava StreamSet](https://developers.strava.com/docs/reference/#api-models-StreamSet)
		streams = self.client.get_activity_streams(activity_id,self.athlete.id)

		#streams.store_locally()
		#to store the stream locally in C:\Users\gaelv\.stravadata\streams_134706

		#streams.set_index("time", inplace = True) 

		streams["dt"] = pd.to_timedelta(streams["time"], unit='s')

		#set a datetime index 
		streams.index = pd.TimedeltaIndex(streams["dt"], name = "datetime")

		'''
		print("streams : ")
		print(str(streams))
		'''

		#sns.set()
		sns.set(style="darkgrid")

		'''
		fig = plt.figure(figsize=(11,8))
		fig = sns.boxplot(streams.heartrate)
		sns.lmplot('time', 'watts', data=streams, fit_reg=False)
		sns.kdeplot(streams.time, streams.watts)
		sns.lineplot('time', 'watts', data=streams, marker=None, markerfacecolor='black', markersize=1, color='black', linewidth=2)
		sns.lineplot('time', 'heartrate', data=streams, marker=None, markerfacecolor='darkblue', markersize=1, color='darkblue', linewidth=2)
		plt.legend()
		sns.relplot(x="time", y="heartrate", hue="watts", estimator=None, kind="line", data=streams);
		sns.lineplot('time', 'heartrate', data=streams, marker="x", markerfacecolor='red', markersize=2, color='black', linewidth=2)
		'''

		'''
		heartrate = streams["heartrate"]
		print(type(heartrate))
		'''

		# filtering
		'''
		masque = streams.heartrate.notnull() 
		streams2 = streams[masque]
		print(streams2)
		print(type(streams2))
		'''


		#streams.plot(kind='line',x='time',y='heartrate',color='black',title='view the gpx', marker='x')
		#plt.show()

		# upscaling if all in the raw data
		resampled  = streams.resample('1s').interpolate(method="linear").fillna(method='ffill')

		# in Watts column, replace nan by 0
		resampled["watts"].fillna(0, inplace = True)

		# test is nan values exist
		'''
		resampled_only_nan = resampled[resampled.isna().any(axis=1)]
		print(str(resampled_only_nan))
		'''

		# Moyenne mobile
		'''resampled["5s"] = resampled["watts"].rolling(5).mean()
		resampled["30s"] = resampled["watts"].rolling('30s').mean()
		resampled["60s"] = resampled["watts"].rolling('60s').mean()'''

		df_stat = pd.DataFrame(
			[1, 3, 5, 10, 20, 30, 60, 120, 180, 300, 480, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300, 3600],
			columns = ['isec'])
			
		df_stat["duration"] = pd.to_datetime(df_stat["isec"], unit='s')

		#df_stat["bis"] = 4

		df_stat["index_max"] = df_stat.apply(lambda row: row["isec"]**2, axis=1)

		# to compute the index of the max
		df_temp = resampled.copy()
		df_temp.reset_index(drop = True, inplace = True)

		#print(str(df_temp))

		indice1 = df_temp["watts"].rolling(10).mean().idxmax()
		print("indice for CP10sec : " , indice1)
		#compute hrm mean from the index
		print(df_temp.iloc[indice1-10+1:indice1+1]["heartrate"].mean())

		df_stat['mean_watts'] = df_stat.apply(lambda row: resampled["watts"].rolling(row["isec"]).mean().max(), axis=1)
		df_stat['index_max'] = df_stat.apply(lambda row: df_temp["watts"].rolling(row["isec"]).mean().idxmax(), axis=1)
		df_stat['hrm_mean'] = df_stat.apply(lambda row: df_temp.iloc[row["index_max"]-row["isec"]+1:row["index_max"]+1]["heartrate"].mean() , axis=1)
		df_stat['cad_mean'] = df_stat.apply(lambda row: df_temp.iloc[row["index_max"]-row["isec"]+1:row["index_max"]+1]["cadence"].mean() , axis=1)
		#df_stat['mean_hrm'] = df_stat.apply(lambda row: resampled["heartrate"].rolling(row["isec"]).mean().mean(), axis=1)

		#df_stat.to_csv(r'D:\python\data\toto.csv', index = True, header=True)

		#set a datetime index 
		#df_stat.index = pd.TimedeltaIndex(df_stat["duration"], name = "datetime")

		#print(str(resampled))
		#print(str(df_stat))
		
		return df_stat