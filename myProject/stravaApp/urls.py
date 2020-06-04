from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'byMonth/', 				views.viewByMonth, name='viewByMonth'),
	url(r'YearProgression/', 		views.viewYearProgression, name='viewYearProgression'),
	url(r'', 						views.viewByMonth, name='viewByMonth'),
]


