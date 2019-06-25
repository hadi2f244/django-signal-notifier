from django.urls import path

from .views import *

app_name = 'Publish'

urlpatterns = [
	# ProductType
	path('1', index1, name='index1'),
	path('2', index2, name='index2'),
	path('3', index3, name='index3'),
	]