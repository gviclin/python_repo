# some_file.py
import sys
import os

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd()+"/stravaio")

#sys.path.append('./')

import pandas as pd
import numpy as np

import datetime
import time

from critical_power import CriticalPower
from activity import Activity



#get an instance of CriticalPower
cp = CriticalPower()
#HT  : 3330576768
#CAP : 3136818310
# Get critical power matrix
df = cp.get_cp_list_by_id(3330576768)
cp.show_plot(df)

'''
act = Activity()
act.get_activities()
'''

