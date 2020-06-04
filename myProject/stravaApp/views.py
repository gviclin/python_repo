from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings

import os
import sys
import json
import glob
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objs as go
import plotly.offline as offline
#from plotly.graph_objs import Scatter

from main_django import getStatByMonth
from main_django import getStatAnnual

# Create your views here.
def viewByMonth(request):
	#print (settings.BASE_DIR)	
	#print(sys.path)
	'''f_name = os.path.join(f"C:/Users/gaelv/.stravadata", f"global_data_134706.parquet")
	
	#print (f_name)
	df = pd.read_parquet(f_name)
	
	html= df.to_html'''
	
	print("")
	
	df = getStatByMonth()
	
	print (df)
	
	html = df.to_html()
	
	'''return HttpResponse("""
        <h1>Bienvenue sur mon blog !</h1>
        <p>Les crêpes bretonnes ça tue des mouettes en plein vol !</p>
    """)'''
	return render(request, 'byMonthStrava.html', locals() )
	
def viewYearProgression(request):
	
	html = ""
	
	df = getStatAnnual()
	
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
		width=1300,
		height=650,
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

	
	return render(request, "byYearStrava.html", context={'plot_div': plot_div})
'''
	return HttpResponse("""
        <h1>Bienvenue sur mon blog !</h1>
        <p>Les crêpes bretonnes ça tue des mouettes en plein vol !</p>
    """)
	'''
	