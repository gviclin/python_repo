from django.conf.urls import include, url
from . import views


urlpatterns = [
	url(r'login/', 					views.viewLogin,	name='viewLogin'),
	url(r'post_ajax/', 				views.post_ajax,	name='post_ajax'),
	url(r'sync_ajax/', 				views.sync_ajax,	name='sync_ajax'),
	url(r'^setting/$', 				views.viewSettingPost,		name='viewSettingPost'),
	#url(r'login/?state=&code=(?P<token>[a-zA-Z0-9_]+)&scope=.*$', 	views.viewLogin, name='viewLogin'),
	#url(r'login/?state=<str:state>&code=<str:token>&scope=<str:scope>', 	views.viewLogin, name='viewLogin'),
	url(r'', 						views.index, name='#'),
]


