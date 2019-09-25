from django.shortcuts import render
from django_eventstream import send_event
from .models import UpdateMessages, Messages
from django_signal_notifier.models import BasicUser as User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def test_notifications(request):
	count_update = UpdateMessages.objects.filter(user_id=request.user.id).count()
	return render(request, 'event_test.html', {"number": count_update})


@csrf_exempt
def update_message_view(request, user_id=None, message_id=None):
	if request.method == "GET":
		result = {}
		if user_id:
			result['status'] = 'ok'
			result['data'] = {}
			notifications = UpdateMessages.objects.filter(user_id=user_id)
			for number, notif in enumerate(notifications):
				result['data'][number] = {"context": notif.context, 'guid': notif.guid}
		else:
			result["status"] = "pleas set user id"
		return JsonResponse(result)
	elif request.method == "DELETE":
		print(type(user_id), message_id)
		try:
			notifications = UpdateMessages.objects.filter(user_id=user_id)
			notifications[int(message_id)].delete()
		except UpdateMessages.DoesNotExist:
			return JsonResponse({"status": "user id is not correct"})
		return JsonResponse({"salam": "bisalam"})
	return render(request, "Salam")


def messages_view(request, user_id=None):
	if request.method == "GET":
		result = {}
		if user_id:
			result['status'] = 'ok'
			result['data'] = {}
			messages = Messages.objects.filter(user_receivers__id=user_id)
			for number, message in enumerate(messages):
				result['data'][number] = {'context': message.context}
			return JsonResponse(result)
	return JsonResponse({"1": "2"})
