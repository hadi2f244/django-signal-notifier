from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django_eventstream import send_event
from .models import Messages
from django_signal_notifier.models import BasicUser as User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def test_notifications(request):
	count_update = Messages.objects.filter(user_receiver_id=request.user.id, is_read=False).count()
	return render(request, 'event_test.html', {"number": count_update})


@csrf_exempt
@login_required
def unread_messages_view(request, message_id=None):
	if request.method == "GET":
		result = dict()
		result['status'] = 'OK'
		result['data'] = list()
		messages = Messages.objects.filter(is_read=False, user_receiver_id=request.user.id)
		for message in messages:
			result['data'].append({"context": message.context, 'uuid': message.uuid})
		return JsonResponse(result)
	elif request.method == 'DELETE':
		if message_id is None:
			return JsonResponse({"status": "set message id"})
		try:
			message = Messages.objects.get(user_receiver_id=request.user.id, uuid=message_id, is_read=False)
			message.is_read = True
			message.save()
		except Exception as e:
			return JsonResponse({"status": str(e)})
		return JsonResponse({"status": "Message read"})


def messages_view(request):
	message_list = Messages.objects.filter(user_receiver_id=request.user.id)
	page = request.GET.get("page", 1)
	paginator = Paginator(message_list, 10)
	try:
		messages = paginator.page(page)
	except PageNotAnInteger:
		messages = paginator.page(1)
	except EmptyPage:
		messages = paginator.page(paginator.num_pages)
	return render(request, 'test_message_list.html', {'messages': messages})
