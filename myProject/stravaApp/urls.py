from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'byMonth/', 				views.viewByMonth, name='viewByMonth'),
	url(r'yearProgression/', 		views.viewYearProgression, name='viewYearProgression'),
	url(r'login/', 					views.viewLogin, name='viewLogin'),
	#url(r'login/?state=&code=(?P<token>[a-zA-Z0-9_]+)&scope=.*$', 	views.viewLogin, name='viewLogin'),
	#url(r'login/?state=<str:state>&code=<str:token>&scope=<str:scope>', 	views.viewLogin, name='viewLogin'),
	url(r'', 						views.viewByMonth, name='#'),
]


