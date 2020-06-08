from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.conf import settings

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
#from plotly.graph_objs import Scatter

from main_django import getStatByMonth
from main_django import getStatAnnual

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def post_ajax(request):
	activityType = "No value"
	statType = "No value"
	response = {"log":"No log"}
	html = ""
	listType = []
	
	if request.method == "POST":
		if 'activityType' in request.POST:
			activityType = request.POST['activityType']	
			response["log"]  = "Activity type : <" + activityType + ">"
		if 'statType' in request.POST:
			statType = request.POST['statType']	
			response["log"]  = response["log"] + " Stat type : <" + statType  +">"
		
	if statType=="month":
		if activityType=="run":
			listType.append("Run")
		elif activityType=="ride":
			listType.append("Ride")
			listType.append("VirtualRide")
			
		df = getStatByMonth(listType)
		html = 	df.to_html()
			
	elif statType=="year":
		if activityType=="run":
			listType.append("Run")
		elif activityType=="ride":
			listType.append("Ride")
			listType.append("VirtualRide")
			
		html = generateGraph(listType)		
		
	response["data"] = html

	return JsonResponse(response, status = 200)
	

# Create your views here.
def viewLogin(request):
	actif = 3
	
	
	#url = request.path
	#Get param :
	if 'code' in request.GET:
		token = request.GET['code']	
		request.session['token'] = token
		
		# Number of visits to this view, as counted in the session variable.
		num_visits = request.session.get('num_visits', 0)
		request.session['num_visits'] = num_visits + 1
		
		return render(request, 'loginStrava.html', locals() )
	else:
		return HttpResponseRedirect("http://www.strava.com/oauth/authorize?client_id=9402&response_type=code&redirect_uri=http://127.0.0.1:8000/strava/login/&approval_prompt=force&scope=read,activity:read_all")



	
def viewByMonth(request):
	actif = 1
	#print (settings.BASE_DIR)	
	#print(sys.path)
	'''f_name = os.path.join(f"C:/Users/gaelv/.stravadata", f"global_data_134706.parquet")
	
	#print (f_name)
	df = pd.read_parquet(f_name)
	
	html= df.to_html'''
	
	if 'actType' in request.GET:
		activityType = request.GET['actType']	
		request.session['activityType'] = activityType
	else:
		activityType = request.session.get('activityType', "run")
		print("")
		
		#df = getStatByMonth()
		
		#print (df)
		
		html = 	None#df.to_html()
		

		
		'''return HttpResponse("""
			<h1>Bienvenue sur mon blog !</h1>
			<p>Les crêpes bretonnes ça tue des mouettes en plein vol !</p>
		""")'''
	return render(request, 'byMonthStrava.html', locals() )
	
def viewYearProgression(request):
	actif = 2
	#plot_div = generateGraph(["run"])

	return render(request, "byYearStrava.html", locals())

	
def generateGraph(list):
	html = ""
	
	df = getStatAnnual(list)
	
	listLines = df["year"].unique()
	
	graphList = []
	for line in listLines:
		filter = df["year"] == line
		dfFilter = df[filter]	
	
		graph = go.Scatter(
			x=dfFilter["date"],
			y=dfFilter["cumul_dist"],
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
			)
		#, marker_color='green')
		
		graphList.append(graph)
		
	dtick1 = 100
		
	layout = go.Layout(
		title="Cumulative km",
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
	


