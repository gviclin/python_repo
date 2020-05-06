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

	def load_all_activities(self,athlete_id):
		"""Get stat_by_year 

		Returns
		-------
		todo
		"""
		pp = pprint.PrettyPrinter(indent=4)
		# retreive the directory
		strava_dir = dir_stravadata()
		activities_dir = os.path.join(strava_dir, f"summary_activities_{athlete_id}")
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
					file_data.pop('total_elevation_gain', None)
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
		
		df['d'] = round(df['distance'] / 1000,1)
		
		#df = df.reindex(columns=sorted(df.columns))
		column_list = ['id', 'date','name', 'distance','elapsed_time','moving_time']
		list_col = (column_list + [a for a in df.columns if a not in column_list] ) 
		#print(str(list_col))
		df = df.reindex(columns=list_col)
		
		df.sort_values(by='date')
		
		'''#display all types
		df_by_type = df.groupby(['type']).count()
		df_by_type.to_html('temp.html')'''
		
		
		# Filter run activities
		filter = df["type"] == "Run"
		df_runnning = df[filter]
		
		df_by_month = df_runnning.groupby(['year','month']).sum()

		
		df_by_month.to_html('temp.html')
		df_by_month.to_excel("stat_by_month.xlsx")  
		#print(tabulate(df, headers='keys', tablefmt='psql'))
		#pp.pprint(file_data)	
		
		#print(df.dtypes)
		

		'''
		fig = df.iplot(asFigure=True, xTitle="Time",
                    yTitle="Distance", title="The Figure Title", x='date',y=['d','month'],
					mode = "lines+markers")
		fig.show()'''
		
		'''df=cf.datagen.lines(4)
		fig = df.iplot(asFigure=True, hline=[2,4], vline=['2015-02-10'])
		fig.show()'''
		
		self.logger.debug("end of stat_by_year")
	


