#import os
import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import signal
import datetime

from stravaio import strava_oauth2
from stravaio import StravaIO


STRAVA_CLIENT_ID = 9402
STRAVA_CLIENT_SECRET = "7960741d3c1563506e073c364e71473c5da1405c"
# STRAVA_ACCESS_TOKEN = "2bdb80afaaef6d81706ac2aa1a0eb04b84025822"

# print(type(STRAVA_CLIENT_ID))
# print(type(STRAVA_CLIENT_SECRET))

try:
	myFile = open('access_token','r')

except IOError:

	token  = strava_oauth2(client_id=STRAVA_CLIENT_ID, client_secret=STRAVA_CLIENT_SECRET)	

	print ("token :" + str(type(token)))
	myFile = open('access_token','w')
	myFile.write(token["access_token"])
	myFile.close()
	myFile = open('access_token','r')
	
except:
    print("Unexpected error:", sys.exc_info()[0])

finally:
	myFile.close

access_token = myFile.read()
# print ('STRAVA_ACCESS_TOKEN : ' + str (access_token))

client = StravaIO(access_token=access_token)
print ("client :" + str(type(client)))

# Get logged in athlete (e.g. the owner of the token)
# Returns a stravaio.Athlete object that wraps the
# [Strava DetailedAthlete](https://developers.strava.com/docs/reference/#api-models-DetailedAthlete)
# with few added data-handling methods
athlete = client.get_logged_in_athlete()


# Dump athlete into a JSON friendly dict (e.g. all datetimes are converted into iso8601)
athlete_dict = athlete.to_dict()

# Store athlete infor as a JSON locally (~/.stravadata/athlete_<id>.json)
athlete.store_locally()

# Get locally stored athletes (returns a generator of dicts)
local_athletes = client.local_athletes()





# Get list of athletes activities since a given date (after) given in a human friendly format.
# Kudos to [Maya: Datetimes for Humans(TM)](https://github.com/kennethreitz/maya)
# Returns a list of [Strava SummaryActivity](https://developers.strava.com/docs/reference/#api-models-SummaryActivity) objects
#list_activities = client.get_logged_in_athlete_activities(after='last week')

# Obvious use - store all activities locally
#for a in list_activities:
#    activity = client.get_activity_by_id(a.id)
 #   activity.store_locally()

activity = client.get_activity_by_id(3330576768)
print(str(activity))
 

	# Returns a stravaio.Streams object that wraps the 
# [Strava StreamSet](https://developers.strava.com/docs/reference/#api-models-StreamSet)
#streams = client.get_activity_streams(3186020006,134706)
streams = client.get_activity_streams(3330576768,134706)
#HT  : 3330576768
#CAP : 3136818310

#streams.store_locally()
#to store the stream locally in C:\Users\gaelv\.stravadata\streams_134706

#streams.set_index("time", inplace = True) 

streams["dt"] = pd.to_timedelta(streams["time"], unit='s')

#set a datetime index 
streams.index = pd.TimedeltaIndex(streams["dt"], name = "datetime")

'''
print("streams : ")
print(str(streams))
'''

#sns.set()
sns.set(style="darkgrid")

'''
fig = plt.figure(figsize=(11,8))
fig = sns.boxplot(streams.heartrate)
sns.lmplot('time', 'watts', data=streams, fit_reg=False)
sns.kdeplot(streams.time, streams.watts)
sns.lineplot('time', 'watts', data=streams, marker=None, markerfacecolor='black', markersize=1, color='black', linewidth=2)
sns.lineplot('time', 'heartrate', data=streams, marker=None, markerfacecolor='darkblue', markersize=1, color='darkblue', linewidth=2)
plt.legend()
sns.relplot(x="time", y="heartrate", hue="watts", estimator=None, kind="line", data=streams);
sns.lineplot('time', 'heartrate', data=streams, marker="x", markerfacecolor='red', markersize=2, color='black', linewidth=2)
'''

'''
heartrate = streams["heartrate"]
print(type(heartrate))
'''

# filtering
'''
masque = streams.heartrate.notnull() 
streams2 = streams[masque]
print(streams2)
print(type(streams2))
'''



#streams.plot(kind='line',x='time',y='heartrate',color='black',title='view the gpx', marker='x')
#plt.show()

# upscaling if all in the raw data
resampled  = streams.resample('1s').interpolate(method="linear").fillna(method='ffill')

# in Watts column, replace nan by 0
resampled["watts"].fillna(0, inplace = True)

# test is nan values exist
'''
resampled_only_nan = resampled[resampled.isna().any(axis=1)]
print(str(resampled_only_nan))
'''

# Moyenne mobile
'''resampled["5s"] = resampled["watts"].rolling(5).mean()
resampled["30s"] = resampled["watts"].rolling('30s').mean()
resampled["60s"] = resampled["watts"].rolling('60s').mean()'''

df_stat = pd.DataFrame(
	[1, 3, 5, 10, 20, 30, 60, 120, 180, 300, 480, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300, 3600],
	columns = ['isec'])
	
df_stat["duration"] = pd.to_datetime(df_stat["isec"], unit='s')

#df_stat["bis"] = 4

df_stat["index_max"] = df_stat.apply(lambda row: row["isec"]**2, axis=1)

# to compute the index of the max
df_temp = resampled.copy()
df_temp.reset_index(drop = True, inplace = True)

#print(str(df_temp))

indice1 = df_temp["watts"].rolling(10).mean().idxmax()
print("indice for CP10sec : " , indice1)
#compute hrm mean from the index
print(df_temp.iloc[indice1-10+1:indice1+1]["heartrate"].mean())

df_stat['mean_watts'] = df_stat.apply(lambda row: resampled["watts"].rolling(row["isec"]).mean().max(), axis=1)
df_stat['index_max'] = df_stat.apply(lambda row: df_temp["watts"].rolling(row["isec"]).mean().idxmax(), axis=1)
df_stat['hrm_mean'] = df_stat.apply(lambda row: df_temp.iloc[row["index_max"]-row["isec"]+1:row["index_max"]+1]["heartrate"].mean() , axis=1)
df_stat['cad_mean'] = df_stat.apply(lambda row: df_temp.iloc[row["index_max"]-row["isec"]+1:row["index_max"]+1]["cadence"].mean() , axis=1)
#df_stat['mean_hrm'] = df_stat.apply(lambda row: resampled["heartrate"].rolling(row["isec"]).mean().mean(), axis=1)

df_stat.to_csv(r'D:\python\data\toto.csv', index = True, header=True)

#set a datetime index 
#df_stat.index = pd.TimedeltaIndex(df_stat["duration"], name = "datetime")

#print(str(resampled))
print(str(df_stat))

'''plt.plot(df_stat["duration"], df_stat["mean_watts"], 'x-')
plt.gcf().autofmt_xdate()
myFmt = mdates.DateFormatter('%H:%M:%S')
plt.gca().xaxis.set_major_formatter(myFmt)
#plt.gca().set_xscale('log')
plt.grid(True)'''

#plt.legend(['original', 'resampledpled'], loc='best')
plt.show()

'''
print(resampled["watts"].rolling(5).mean().max())'''

# display the plot
'''begin = streams[streams.time < streams.size]	
begin2 = resampled[resampled.time < streams.size]

plt.plot(begin["time"], begin["watts"], 'go-')
plt.plot(begin2["time"], begin2["watts"], 'x')
plt.legend(['original', 'resampledpled'], loc='best')
plt.show()'''

#, color='green'
'''
x = np.linspace(0, 10, 20, endpoint=False)
y = np.cos(-x**2/6.0)
f = signal.resampledple(y, 100)
xnew = np.linspace(0, 10, 100, endpoint=False)

plt.plot(x, y, 'go-', xnew, f, '.-', 10, y[0], 'x')
plt.legend(['data', 'resampledpled'], loc='best')
plt.show()
'''


# stream is a panda dataframe
'''
print(type(streams))

print(streams.info())

# Access streams using the dot notation
cadence = streams.cadence
print(str(cadence))
print("cadence : ")

#print(str(cadence))
'''

# Dump streams into a JSON friendly dict
# streams_dict = streams.to_dict()
#print(str(streams_dict))


# Store streams locally (~/.stravadata/streams_<athlete_id>/streams_<id>.parquet) as a .parquet file, that can be loaded later using the
# pandas.read_parquet()
#streams.store_locally()
'''
famille_panda = [
   [100.555, 5  , 20, 80], # maman panda
   [50 , 2.5, 10, 40], # bébé panda
   [110.1, 6  , 22, 80], # papa panda
]
print(type(famille_panda))
famille_panda_numpy = np.array(famille_panda)

famille_panda_df = pd.DataFrame(famille_panda_numpy,
                                index = ['maman', 'bebe', 'papa'],
                                columns = ['pattes', 'poil', 'queue', 'ventre'])
print(' np : ') 
print(famille_panda_numpy)
print(' pd :') 
print(famille_panda_df)

print (famille_panda_df.ventre)
print (famille_panda_df.ventre.values)

print(famille_panda_df[famille_panda_df["ventre"] == 80])

r = np.reshape(np.arange(256*256)%256,(256,256))  # 256x256 pixel array with a horizontal gradient from 0 to 255 for the red color channel
print(r)

g = np.zeros_like(r)  # array of same size and type as r but filled with 0s for the green color channel
b = r.T # transposed r will give a vertical gradient for the blue color channel
	
cv2.imwrite('gradients.png', np.dstack([b,g,r]))  # OpenCV images are interpreted as BGR, the depth-stacked array will be written to an 8bit RGB PNG-file called 'gradients.png'


titanic = sns.load_dataset('titanic')

print("pivot ::" + str(titanic.pivot_table('survived', index='sex', columns='class', aggfunc="sum")))
'''