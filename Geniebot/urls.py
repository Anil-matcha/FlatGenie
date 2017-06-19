from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', jokebot.as_view()),
    #url(r'^find_flats_by_location_and_rent/$', views.find_flats_by_location_and_rent),   
]