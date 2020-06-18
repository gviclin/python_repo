from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.conf import settings
from .models import User

from datetime import datetime, tzinfo
import pytz

from loguru import logger
from django.utils.timezone import make_aware

import os
import sys
import json
import glob
import pandas as pd
import numpy as np
import re

import plotly.express as px
import plotly.graph_objs as go
import plotly.offline as offline

from stravaApp.stravaInterface import *

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def post_ajax(request):
	logger.debug("======> post_ajax. URL <" + request.path + ">")
	activityType = "No value"
	statType = "No value"
	response = {"log":""}
	html = ""
	listType = []
	
	#check if logged
	access_token = request.session.get('ACCESS_TOKEN', None) 
	
	# retreive user table
	user_id = request.session.get('user_id', None) 
	user = User()	
	try:
		user = User.objects.get(user_id=user_id)
	except user.DoesNotExist:
		user = None
	
	if  access_token is not None and id is not None:	
	
		if request.method == "POST":
			if 'activityType' in request.POST:
				activityType = request.POST['activityType']	
				response["log"]  = "Activity type : <" + activityType + ">"
			if 'pageType' in request.POST:
				statType = request.POST['pageType']	
				response["log"]  = response["log"] + " Stat type : <" + statType  +">"
			
		if statType=="month":
			if activityType.find("run")!=-1:
				listType.append("Run")
			if activityType.find("ride")!=-1:
				listType.append("Ride")
				listType.append("VirtualRide")
			
			if len(activityType)>0:
				df = getStatByMonth(user_id, listType)
				html = 	df.to_html()
				
		elif statType=="year":
			if activityType.find("run")!=-1:
				if user:
					objList = [user.year_run_objective]
				else:
					objList = [500]
				#objList = [1400,1600]
				listType.append("Run")
			if activityType.find("ride")!=-1:
				if user:
					objList = [user.year_ride_objective]
				else:
					objList = [500]
				#objList = [6000,7000]
				listType.append("Ride")
				listType.append("VirtualRide")
				
			if len(activityType)>0:
				html = generateGraph(user_id, listType, objList)		
				
		elif statType=="setting":
			html = "Settings"
			
		elif statType=="logout":
			#logoff
			
			access_token = request.session.get('ACCESS_TOKEN', None)
			
			if 	access_token is not None:
				#logger.debug(f"logout. Access token <" + access_token + ">")		
				logoff(access_token)
				
			request.session['ACCESS_TOKEN'] = None
				
			html = "Logout"	
			
		response["data"] = html
	
	#else:
		# not logged
		#response["log"]  = "Not logged"


	return JsonResponse(response, status = 200)
	

# Create your views here.
def viewLogin(request):
	logger.debug("======> viewLogin. URL <" + request.path + ">")
	actif = 3	
	if os.environ.get('DEV'):
		dev = True
	else:
		dev = False
		
	isLogged = True
	name = "Login"
	
	#url = request.path
	#Get param :
	if 'code' in request.GET:
		user_code = request.GET['code']	
		
		logger.debug(f" user_code <" + str(user_code) + ">")		
		
		#check if already logged
		temp_access_token = request.session.get('ACCESS_TOKEN', None) 
				
		if  temp_access_token is None:
					
			'''# Number of visits to this view, as counted in the session variable.
			num_visits = request.session.get('num_visits', 0)
			request.session['num_visits'] = num_visits + 1'''
			
			access_token = login(user_code)
			
			if access_token is not None or not access_token:			
				#store the activity instance
				request.session['ACCESS_TOKEN'] = access_token				

			else:
				isLogged =  False
		
		else:
			access_token = 	temp_access_token			

	else:
		html = ""
		isLogged =  False
		
	
	if isLogged:	
		#retrieve the athlete infos and save it in db
		athlete = getAthlete(access_token)	
		if athlete:	
			# store athlete id in session		
			request.session['user_id'] = int(athlete["id"])	
			# store athlete infos in DB
			user = User()
			try:
				user = User.objects.get(user_id=int(athlete["id"]))
			except user.DoesNotExist:
				user = None
			
			if not user:
				user = User()
				user.user_id = athlete["id"]
				
			user.django_user = request.user
			user.firstname = athlete["firstname"]
			user.lastname = athlete["lastname"]
			user.weight = athlete["weight"]
			user.sex = athlete["sex"] if athlete["sex"] else ""
			user.country = athlete["country"]
			user.state = athlete["state"]
			user.city = athlete["city"]
			user.follower_count = int(athlete["follower_count"])
			user.friend_count = int(athlete["friend_count"])
			user.measurement_preference = athlete["measurement_preference"]
			user.ftp = int(athlete["ftp"] if athlete["ftp"] else -1)
			user.updated_date = timezone.now()
			user.strava_creation_date = make_aware(datetime.datetime.strptime(athlete["created_at"], '%Y-%m-%dT%H:%M:%SZ'),timezone=timezone.utc)
			user.save()
		else:
			logoff(access_token)
			request.session['ACCESS_TOKEN'] = None
			#html = f"Error in calling Strava API"
			name ="Login"		
		
		return index(request, actif = 1)
	else:
		html = "Login failed ! "
		request.session['ACCESS_TOKEN'] = None

	#logger.debug(f"session_key : "+ request.session.session_key)
		
	return render(request, 'baseStrava.html', locals() )


	
def index(request, actif = 1):
	logger.debug("======> index. URL <" + request.path + ">")
	# By default, stat by month
	#actif = 1	
	if os.environ.get('DEV'):
		dev = True
	else:
		dev = False
				
	#check if logged
	access_token = request.session.get('ACCESS_TOKEN', None) 			
	if  access_token is not None:
		isLogged =  True
		
		# retreive user table
		user_id = request.session.get('user_id', None) 
		user = User()	
		try:
			user = User.objects.get(user_id=user_id)
		except user.DoesNotExist:
			user = None
	
		if user: 
			#Retreive strava datas
			#endDate = make_aware(datetime.datetime.utcnow() +  timedelta(hours=24),timezone=timezone.utc)
			endDate = datetime.datetime.utcnow() +  timedelta(hours=24)
			#logger.debug("endDate : " + endDate.tzname()) 			
			
			if user.last_activity_date is not None:		
				#logger.debug("--> last_activity_date is not null")			
				startDate = user.last_activity_date  +  timedelta(seconds=1)
				#unset the timezone !!!
				startDate = startDate.replace(tzinfo=None)
			else:
				#logger.debug("--> last_activity_date is null") #timezone=timezone.utc
				startDate = datetime.datetime(2000, 1, 1, 0, 0 ,0)

			
			'''endDate = datetime.datetime.utcnow() +  timedelta(hours=24) 
			startDate = endDate - timedelta(days=31)'''
			
			#startDate = endDate - timedelta(days=31*12*15)
			range = RetreiveFromDateInterval(access_token, user.user_id, startDate, endDate)	
			
			#store the date range in db
			user = User.objects.get(user_id=int(user.user_id))
			logger.debug("-> result : activity from " + str(range[0]) + " to " + str(range[1]) + ". Number " + str(range[2]))
			
			if range[0]:
				user.first_activity_date = make_aware(range[0], timezone=timezone.utc)
			else:
				user.first_activity_date = None
			if range[1]:
				user.last_activity_date = make_aware(range[1], timezone=timezone.utc)
			else:
				user.last_activity_date = None
			
			user.act_number = range[2] if range[2] else 0
			user.save()
			
			name = user.firstname + " " + user.lastname + " <i class=\"fa fa-caret-down\"></i>"
			#html = athlete	


	else:
		isLogged =  False
	return render(request, 'baseStrava.html', locals() )
	
def generateGraph(id, list, objList):
	html = ""
	
	df = getStatAnnual(id, list, objList)
	
	listLines = df["year"].unique()
	
	graphList = []
	for line in listLines:
		filter = df["year"] == line
		dfFilter = df[filter]	
		
		# objectif line
		if line.find("km") != -1:
			graph = go.Scatter(
				x=dfFilter["start_date"],
				y=dfFilter["cumul_dist"],
				name=line,
				opacity=1,
				mode="lines",
				line=dict(dash="dashdot", width=3), # dot, dash, dashdot
				text = line,
				marker=dict(
					symbol="circle",
					size=6,
					line=dict(width=0,
						color='DarkSlateGrey'
						),
				),		
				hovertemplate = 'Objective : %{data.name}<br>%{x|%d/%m}<br>%{y:.1f} kms<extra></extra>',			
			)
		else:
			# Normal line
			graph = go.Scatter(
				x=dfFilter["start_date"],
				y=dfFilter["cumul_dist"],
				customdata=dfFilter["distance"],
				name=line,
				opacity=1,
				mode="markers+lines",
				text = line,
				marker=dict(
					symbol="circle",
					size=6,
					line=dict(width=0,
						color='DarkSlateGrey'
						),
				),			
				line=dict(dash="solid", width=2), # dot, dash, dashdot
				hovertemplate = '%{x|%d/%m}/%{data.name}<br>%{y:.1f} kms<br>Activity : %{customdata:.1f} kms<extra></extra>',
				# https://github.com/d3/d3-3.x-api-reference/blob/master/Time-Formatting.md#format
			)
		
		graphList.append(graph)
		
	dtick1 = 100 if "Run" in list else 1000
		
	layout = go.Layout(
		title="Cumulative km (" + list[0] + ")" ,
		autosize=True,
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
			#type="start_date"
			),
			yaxis = dict(
			title = "Cumul Km",
			nticks =20,
			dtick= dtick1
			),
		)	
	
	plot_div = offline.plot({"data": graphList,
		"layout": layout},
		include_plotlyjs=False,
		output_type='div')

	# bidouille pour créer une fonction de creation du plot
	'''plot_div = re.sub(
		r'window.PLOTLYENV=window.PLOTLYENV',
		r'\r	function displayPlot() {\r		window.PLOTLYENV=window.PLOTLYENV',
		plot_div)   
		
	plot_div = re.sub(
		r' }',
		r' }\r}\r	displayPlot()',
		plot_div)'''
		
		
	

	return plot_div
	
	

