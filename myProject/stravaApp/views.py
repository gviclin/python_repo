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
import cv2
import cufflinks as cf
import plotly.express as px

#from ..main_ride import run

# Create your views here.
def main(request):

	'''f_name = os.path.join(f"C:/Users/gaelv/.stravadata", f"global_data_134706.parquet")
	
	#print (f_name)
	df = pd.read_parquet(f_name)
	
	html= df.to_html'''
	
	print("")
	
	#run()
	
	#print (settings.BASE_DIR)
	
	print(sys.path)

	'''return HttpResponse("""
        <h1>Bienvenue sur mon blog !</h1>
        <p>Les crêpes bretonnes ça tue des mouettes en plein vol !</p>
    """)'''
	return render(request, 'mainStrava.html', {})