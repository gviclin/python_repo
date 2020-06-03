from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.view1, name='view1'),
]