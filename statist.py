import os
import json
import glob
import pandas as pd
import numpy as np
import cv2
import cufflinks as cf
import plotly.express as px

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

	def Compute_the_local_db(self,athlete_id, startdate, enddate):
		""" Compute_the_db 

		Returns
		-------
		todo
		"""
		print("Compute the local db from", startdate.strftime("%Y-%m-%d %H:%M:%S"), "to", enddate.strftime("%Y-%m-%d %H:%M:%S"))
		pp = pprint.PrettyPrinter(indent=4)
		# retreive the directory
		activities_dir = os.path.join(self.strava_dir, f"summary_activities_{athlete_id}")
		if not os.path.exists(activities_dir):
			self.logger.debug("path ",activities_dir,"does not exist !")
			
		#wait = input("PRESS ENTER TO CONTINUE.")
		#quit()

		#self.logger.debug(activities_dir)
		i = 0
		list = []
		# open all files
		for path in Path(activities_dir).iterdir():
			if path.is_file():
				#print("file : ", str(path))
				with open(path) as f:
					file_data = json.load(f)				
					
					dt1 = datetime.datetime.strptime(file_data['start_date_local'], '%Y-%m-%dT%H:%M:%SZ')
					
					if dt1 > startdate and dt1 < enddate:
						#self.logger.debug("open file number : " + str(i))
						#print(dt1)
						
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
		newDf = pd.concat(list)

		newDf['date'] =  pd.to_datetime(newDf['start_date_local'], format='%Y-%m-%dT%H:%M:%SZ')
		newDf.drop('start_date_local', axis=1,inplace=True)
		
		#add year / month columns
		newDf['year'] = pd.DatetimeIndex(newDf['date']).year
		newDf['month'] = pd.DatetimeIndex(newDf['date']).month
		
		newDf['month'] = newDf['month'].apply(str)
		newDf['year'] = newDf['year'].apply(str)
		
		newDf.sort_values(by='date', inplace=True, ascending=True)
		
		newDf['distance'] = round(newDf['distance'] / 1000,3)
		
		#newDf = newDf.reindex(columns=sorted(newDf.columns))
		column_list = ['id', 'date','name', 'distance','elapsed_time','moving_time']
		list_col = (column_list + [a for a in newDf.columns if a not in column_list] ) 
		#print(str(list_col))
		newDf = newDf.reindex(columns=list_col)		
		newDf.set_index("id")
		
		f_name = os.path.join(self.strava_dir, f"global_data_{athlete_id}.parquet")		
		
		if not os.path.exists(f_name):
			#self.logger.debug("path ",f_name,"does not exist !")
			df = newDf
		else:
			# Existing dataframe
			existingDf = pd.read_parquet(f_name)	
			
			# Remove datas belong to the given interval
			mask = (existingDf['date'] < startdate) | (existingDf['date'] >= enddate)
			existingDf=existingDf.loc[mask]
			
			# Concatenate the 2 dataframes
			df = pd.concat([existingDf, newDf]).drop_duplicates().reset_index(drop=True)			
			print("Local bd size changed from " + str(len(existingDf)) + " to " + str(len(df)))
		
		#Store the dataframe		
		df.to_parquet(f_name)
		
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
		'''
		df_by_month.to_html(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_by_month_{athlete_id}.html"))
		df_by_month.to_excel(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_by_month_{athlete_id}.xlsx"))
		'''
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
		
		#Create a column with the month string
		df_dist['month_str'] = df_dist.apply(lambda row: datetime.date(1900, int(row["month"]), 1).strftime('%B'), axis=1)
		df_dist.set_index("month_str",inplace=True)
		df_dist.loc["Total"] = df_dist.sum()
		
		df_dist.drop('month',inplace=True,axis=1)
		
		#os.remove(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_distance_{athlete_id}.xlsx"))
		
		df_dist.to_parquet(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_distance_{athlete_id}.parquet"))
		df_dist.to_html(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_distance_{athlete_id}.html"))
		df_dist.to_excel(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_distance_{athlete_id}.xlsx"))
		'''
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
		
		#self.logger.debug("end of stat_by_year")
		
		return df_dist
		
	
	
	def Stat_dist_annual(self,athlete_id, activityType, dist_goal_list = [0]):
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
		
		#df = df[["year","month","date","distance","elapsed_time","moving_time","total_elevation_gain"]]
		df = df[["year","month","date","distance","id"]]
		
		df.id = df.id.astype(int)
		
		df.sort_values(by='date', inplace=True, ascending=True)
		
		df.set_index("date",inplace=True, drop=False)
		
		df['cumul_dist'] = df.groupby(df.index.year)["distance"].cumsum()		
		
		df["date"] = df.apply(lambda row:  row["date"].replace(year = 1904), axis=1)
		
		df = df[["year","month","date","cumul_dist","distance","id"]]
		
		#distance goal
		for goal in dist_goal_list:
			strGoal =   f"{goal} km"
			dt_goal = pd.date_range(datetime.datetime(1904, 1, 1,0,0,0), periods=365, freq='D')
			ts = pd.Series(range(len(dt_goal)), index=dt_goal)
			frame = { 'cumul_dist': ts } 
			result = pd.DataFrame(frame) 
			result["cumul_dist"] = result.apply(lambda row:  goal * row["cumul_dist"] / 364, axis=1)
			#result["distance"] = result.apply(lambda row:  goal / 364, axis=1)
			result.reset_index(inplace=True)
			result['month'] = pd.DatetimeIndex(result['index']).month		
			result['month'] = result['month'].apply(str)
			result['year'] = strGoal
			result['id'] = 0		
			result.rename({'index': 'date'}, axis=1, inplace=True)
			result.set_index(keys="date", inplace=True, drop=False)			
			df = pd.concat([df,result])
		
		print("")
		print("type :",activityType)
		print(df.info(verbose=True))
		print(df)
		
		#print(tabulate(df, headers='keys', tablefmt='psql'))
		#df.to_html(os.path.join(self.strava_dir, f"temp.html"))
		
		# Y axis : distance beetween 2 ticks
		dtick1 = 100 if "Run" in activityType else 1000
		
		fig = px.line(
			df,
			 x="date",
			  y="cumul_dist",
			  line_group="year",
			  color="year",
			  custom_data=["id","year","distance"],
			  #hover_name=df["distance"]
			  #hover_data=["month", "cumul_dist"]
			  )
		#All traces	  
		fig.update_traces(
			mode="markers+lines",
			marker=dict(
				symbol="circle",
				size=6,
				line=dict(width=0,
					color='DarkSlateGrey'
					)
				),			
			line=dict(dash="solid", width=2), # dot, dash, dashdot
			text = df["year"],
			hovertemplate = '%{x}<br> %{y:.1f} kms<br>activity %{customdata[2]:.1f} kms<br>link %{customdata[0]}'			
			)
			
		# Only goal trace
		for goal in dist_goal_list:
			fig.update_traces(
				selector=dict(name=f"{goal} km"),
				mode="lines",
				line=dict(dash="dashdot", width=3), # dot, dash, dashdot
				hovertemplate = '%{x}<br>%{y:.1f} kms'
				)
			
		fig.update_layout(
			title=f"Annual {activityType[0]} Statistics",
			#hovermode="x unified",
			xaxis_tickformat = '%-d-%b',
			legend = dict(
				title="Year :",
				orientation="v",
				itemclick ="toggle",
				itemdoubleclick ="toggleothers"				
				),
			xaxis = dict(
				title = "Month",
				nticks =12
				#tickmode = 'linear',
				#type="date"
			),
			yaxis = dict(
				title = "Cumul Km",
				nticks =20,
				dtick= dtick1
			)
		)	
		
		# create our callback function
		def update_point(trace, points, selector):
			print("toto")
			c = list(scatter.marker.color)
			s = list(scatter.marker.size)
			for i in points.point_inds:
				c[i] = '#bae2be'
				s[i] = 20
				with f.batch_update():
					scatter.marker.color = c
					scatter.marker.size = s

		scatter = fig.data[0]

		#scatter.on_click(update_point)
		
		#df.to_excel(os.path.join(self.strava_dir, f"stat_{'_'.join(activityType)}_annual_distance_{athlete_id}.xlsx"))

		#fig.show()
		
		
		'''fig = df.iplot(asFigure=True, xTitle="Month",
		yTitle="Distance", title="Annual statistics", x="dt",y="cumul_dist",
		mode = "lines")
		fig.show()'''
	
		return df
		
