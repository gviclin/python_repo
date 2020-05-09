import os
import json
import glob
import pandas as pd
import numpy as np
import cv2
import cufflinks as cf

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tick

import seaborn as sns
#from scipy import signalsignal
import datetime
import time
from pathlib import Path
from tabulate import tabulate
import pprint 

from stravaio import dir_stravadata

class Statist():

	def __init__(self, logger):
		self.i = 5
		self.logger = logger
		self.strava_dir = dir_stravadata()

	def Compute_the_db(self,athlete_id):
		""" Compute_the_db 

		Returns
		-------
		todo
		"""
		pp = pprint.PrettyPrinter(indent=4)
		# retreive the directory
		activities_dir = os.path.join(self.strava_dir, f"summary_activities_{athlete_id}")
		if not os.path.exists(activities_dir):
			self.logger.debug("path ",activities_dir,"does not exist !")

		self.logger.debug(activities_dir)
		i = 0
		list = []
		# open all files
		for path in Path(activities_dir).iterdir():
			if path.is_file():
				if i% 100 == 0:
					self.logger.debug("open file number : " + str(i))
				#print("file : ", str(path))
				with open(path) as f:
					file_data = json.load(f)
					
					#filtering datas
					file_data.pop('athlete', None)		
					file_data.pop('map', None)	
					file_data.pop('achievement_count', None)	
					file_data.pop('athlete_count', None)	
					file_data.pop('elev_high', None)	
					file_data.pop('elev_low', None)	
					file_data.pop('external_id', None)	
					file_data.pop('photo_count', None)	
					file_data.pop('total_photo_count', None)	
					file_data.pop('upload_id', None)			
					file_data.pop('end_latlng', None)
					file_data.pop('kudos_count', None)
					file_data.pop('max_speed', None)		
					file_data.pop('max_watts', None)
					file_data.pop('start_date', None)		
					file_data.pop('start_latlng', None)
					file_data.pop('timezone', None)		
					#file_data.pop('total_elevation_gain', None)
					file_data.pop('weighted_average_watts', None)
					file_data.pop('average_speed', None)
					file_data.pop('average_watts', None)
					file_data.pop('comment_count', None)
					file_data.pop('gear_id', None)
					file_data.pop('has_kudoed', None)
					file_data.pop('kilojoules', None)
						
					df_temp = pd.DataFrame(file_data, index=[file_data["id"]])

					list.append(df_temp)
					i +=1
					'''if i >20:
						break'''
		
		#concatenate all dataframe
		df = pd.concat(list)

		df['date'] =  pd.to_datetime(df['start_date_local'], format='%Y-%m-%dT%H:%M:%SZ')
		df.drop('start_date_local', axis=1,inplace=True)
		
		#add year / month columns
		df['year'] = pd.DatetimeIndex(df['date']).year
		df['month'] = pd.DatetimeIndex(df['date']).month
		
		df['month'] = df['month'].apply(str)
		df['year'] = df['year'].apply(str)
		
		df.sort_values(by='date')
		
		df['distance'] = round(df['distance'] / 1000,3)
		
		#df = df.reindex(columns=sorted(df.columns))
		column_list = ['id', 'date','name', 'distance','elapsed_time','moving_time']
		list_col = (column_list + [a for a in df.columns if a not in column_list] ) 
		#print(str(list_col))
		df = df.reindex(columns=list_col)
		
		#Store the dataframe
		f_name = f"global_data_{athlete_id}.parquet"
		df.to_parquet(os.path.join(self.strava_dir, f_name))
		
		#Store the dataframe in excell file
		df.to_excel(os.path.join(self.strava_dir, f"global_data_{athlete_id}.xlsx"))
		
		#Store the dataframe in html file
		df.to_html(os.path.join(self.strava_dir, f"global_data_{athlete_id}.html"))
		
	def Stat_dist_by_month(self,athlete_id, activityType):
		""" Compute_the_db 
		activityType : "Run", "Hike", "VirtualRide", "VirtualRun", "Walk","Ride"
		Returns
		-------
		Make stat by month and activity type
		"""
		# Read global data file
		f_name = os.path.join(self.strava_dir, f"global_data_{athlete_id}.parquet")
		df = pd.read_parquet(f_name)
		
		# Filter by type of activity
		filter = df["type"].isin(activityType)
		df_type = df[filter]		
	
		df_by_month = df_type.groupby(['year','month']).sum()
		
		df_by_month = df_by_month[["distance","elapsed_time","moving_time","total_elevation_gain"]]
		
		df_by_month.drop('elapsed_time', axis=1,inplace=True)
		
		df_by_month["avg_speed"] = round(3600 * df_by_month["distance"] / df_by_month["moving_time"],1)
		df_by_month["avg_elev_by_10km"] = round(10 * df_by_month["total_elevation_gain"] / df_by_month["distance"],0)
		
		df_by_month.to_html(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_by_month_{athlete_id}.html"))
		df_by_month.to_excel(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_by_month_{athlete_id}.xlsx"))
		#print(tabulate(df, headers='keys', tablefmt='psql'))
		#pp.pprint(file_data)		
		#print(df.dtypes)

		#stat by month and year
		df_dist = df_by_month[["distance"]]	
		df_dist.reset_index(level="year", inplace=True)
		df_dist.reset_index(level="month", inplace=True)		
		df_dist = df_dist.pivot(index='year', columns='month', values='distance')
		#df_dist.reset_index(inplace=True)	
		
		#add annual stat
		df_dist["total"] = df_dist.sum(axis=1)
		
		df_dist.fillna(0, inplace=True)
		df_dist = df_dist.round(1)

		
		df_dist.to_html(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_distance_{athlete_id}.html"))
		df_dist.to_excel(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_distance_{athlete_id}.xlsx"))
		
	
		'''df=cf.datagen.lines(4)
		fig = df.iplot(asFigure=True, hline=[2,4], vline=['2015-02-10'])
		fig.show()'''
				
		#df_dist["year"] = pd.to_numeric(df_dist["year"])
		#df_dist.set_index("year")
		df_dist.drop('total', axis=1,inplace=True)
		df_dist = df_dist.T
		df_dist.reset_index(inplace=True)
		df_dist["month"] = pd.to_numeric(df_dist["month"])	
		df_dist.sort_values(by='month',inplace =True)		
		
		#df_dist["month_str"] = (datetime.date(1900, df_dist["month"], 1).strftime('%B'))
		df_dist['month_str'] = df_dist.apply(lambda row: datetime.date(1900, int(row["month"]), 1).strftime('%B'), axis=1)
		
		print("")
		print("type :",activityType)
		print(df_dist.info(verbose=True))
		#print(df_dist)
		print(tabulate(df_dist, headers='keys', tablefmt='psql'))
		
		series_x = df_dist["month_str"]
		df_dist.drop("month", axis=1,inplace=True)
		list_month = list(df_dist.columns)
		list_month.remove("month_str")
				
		fig = df_dist.iplot(asFigure=True, xTitle="Month",
		yTitle="Distance", title="By month", x='month_str',y=list_month,
			mode = "lines+markers")
		fig.show()
		
		'''

		
		fig, ax = plt.subplots()
		ax.set_title('Month statistics')
		ax.plot(
				series_x, df_dist, 'x-'
				)
		ax.legend(list(df_dist.columns.values), loc='upper right')
		fig.autofmt_xdate()
		plt.grid(True)			
		plt.show()'''
		
		self.logger.debug("end of stat_by_year")
		
	
	def Stat_dist_annual(self,athlete_id, activityType):
		""" Compute_the_db 
		activityType : "Run", "Hike", "VirtualRide", "VirtualRun", "Walk","Ride"
		Returns
		-------
		Make stat by month and activity type
		"""
		# Read global data file
		f_name = os.path.join(self.strava_dir, f"global_data_{athlete_id}.parquet")
		df = pd.read_parquet(f_name)
		
		# Filter by type of activity
		filter = df["type"].isin(activityType)
		df = df[filter]	
		
		df = df[["year","month","date","distance","elapsed_time","moving_time","total_elevation_gain"]]
		
		df.set_index("date",inplace=True)
		
		df['cumul_dist'] = df.groupby(df.index.year)["distance"].cumsum()
		#df.apply(lambda row: row["227538958"], axis=1)
		df['dt'] = df.index
		
		print("")
		print("type :",activityType)
		print(df.info(verbose=True))
		print(df)
		#print(tabulate(df, headers='keys', tablefmt='psql'))
		df.to_html(os.path.join(self.strava_dir, f"temp.html"))
		
		fig = df.iplot(asFigure=True, xTitle="Month",
		yTitle="Distance", title="By month", x="dt",y="cumul_dist",
		mode = "lines")
		fig.show()
	
		return 
		
