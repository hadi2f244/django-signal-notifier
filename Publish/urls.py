from django.urls import path

from .views import *

app_name = 'Publish'

urlpatterns = [
	# ProductType
	path('1', index1, name='index1'),
	path('2', index2, name='index2'),
	path('3', index3, name='index3'),
	path('set_signal/', set_signal, name='set_signal'),
	path('delete_testmodel/', delete_testmodel, name='delete_testmodel'),
	path('new_testmodel/', new_testmodel, name='new_testmodel'),
]