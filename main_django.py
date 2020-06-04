# some_file.py
import sys
import os

import logging


import pandas as pd
import numpy as np

import datetime
import time
from datetime import timedelta  

from critical_power import CriticalPower
from activity import Activity
from statist import Statist

def getStatByMonth():	
	# create logger
	logger = logging.getLogger('')
	logger.setLevel(logging.DEBUG)
	
	stat = Statist(logger)

	athlete_id = 134706
	
	return stat.Stat_dist_by_month(athlete_id,["Run"])	
	#wait = input("PRESS ENTER TO CONTINUE.")
	
def getStatAnnual():	
	# create logger
	logger = logging.getLogger('')
	logger.setLevel(logging.DEBUG)
	
	stat = Statist(logger)
	
	athlete_id = 134706
	
	return stat.Stat_dist_annual(athlete_id,["Run"],[1400,1600])
	#stat.Stat_dist_annual(athlete["id"],["Run"],[600,700])	
	
	#wait = input("PRESS ENTER TO CONTINUE.")
	

if __name__ == "__main__":
	run()



