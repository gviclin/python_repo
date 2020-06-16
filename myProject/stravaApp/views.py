from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.conf import settings

from loguru import logger

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
	activityType = "No value"
	statType = "No value"
	response = {"log":""}
	html = ""
	listType = []
	
	#check if logged
	access_token = request.session.get('ACCESS_TOKEN', None) 
	id = request.session.get('id', None) 	
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
				df = getStatByMonth(id, listType)
				html = 	df.to_html()
				
		elif statType=="year":
			if activityType.find("run")!=-1:
				objList = [1400,1600]
				listType.append("Run")
			if activityType.find("ride")!=-1:
				objList = [6000,7000]
				listType.append("Ride")
				listType.append("VirtualRide")
				
			if len(activityType)>0:
				html = generateGraph(id, listType, objList)		
				
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
		athlete = getAthlete(access_token)	
		if athlete:		
			request.session['id'] = athlete["id"] 		
			name = athlete["firstname"] + " " + athlete["lastname"] + " <i class=\"fa fa-caret-down\"></i>"
			html = athlete	
		else:
			logoff(access_token)
			request.session['ACCESS_TOKEN'] = None
			html = f"Error in calling Strava API"
			name ="Login"
	
		#logger.debug(f"viewLogin. Access token <" + str(access_token) + ">")		
	else:
		html = "Login failed ! "
		request.session['ACCESS_TOKEN'] = None

	#logger.debug(f"session_key : "+ request.session.session_key)
		
	return render(request, 'loginStrava.html', locals() )


	
def viewByMonth(request):
	actif = 1	
	if os.environ.get('DEV'):
		dev = True
	else:
		dev = False
		
	# Show python path
	'''for p in sys.path:
	print(" - " + p)
	return'''
		
	#check if logged
	access_token = request.session.get('ACCESS_TOKEN', None) 			
	if  access_token is not None:
		isLogged =  True
		#name="Login"
		athlete = getAthlete(access_token)	
		if athlete:		
			request.session['id'] = athlete["id"] 	
			name = athlete["firstname"] + " " + athlete["lastname"] + " <i class=\"fa fa-caret-down\"></i>"
		else:
			logoff(access_token)
			request.session['ACCESS_TOKEN'] = None
			html = f"Error in calling Strava API"
			name ="Login"

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
				x=dfFilter["date"],
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
				x=dfFilter["date"],
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
			#type="date"
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
	
	

