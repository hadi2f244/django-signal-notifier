from django.contrib.auth.models import User
from django.db.models import signals
from django.http import HttpResponse
from django.shortcuts import render

from Publish.models import Book
from django_signal_notifier.models import Trigger, TestModel1

def hello(request):
   text = """<h1>welcome to my app !</h1>"""
   return HttpResponse(text)

def index1(request):
    obj = Book.objects.all()
    return render(request, "index.html", locals())

def index2(request):
    obj = Book.objects.all().select_related("publisher")
    return render(request, "index.html", locals())

def index3(request):
    obj = Book.objects.all().prefetch_related("publisher")
    return render(request, "index.html", locals())

def set_signal(request):
	# schedule_email('Email from sitemessage.', [request.user, 'user2@host.com'])
	user1 = User.objects.first()

	Trigger.save_by_model(
		verb_name="pre_save",
		verb_signal=signals.pre_save,
		action_object=TestModel1,
		actor_object=user1,
		target="test_save_by_model_2",
	)

	Trigger.save_by_model(
		verb_name="post_delete",
		verb_signal=signals.post_delete,
		action_object=TestModel1,
		actor_object=user1,
		target="test_save_by_model_2",
	)

	# TestModel1.objects.create(name="new_test_model", extra_field="extra")
	return HttpResponse("OK")



def delete_testmodel(request):
	TestModel1.objects.all()[0].delete()
	return HttpResponse("TestModel1 is deleted!")

def new_testmodel(request):
	TestModel1.objects.create(name="test")
	return HttpResponse("TestModel1 is created!")
