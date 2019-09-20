from django.shortcuts import render
from django_eventstream import send_event
from .models import UpdateMessages
from django.http import JsonResponse, HttpResponse


def test_notifications(request):
    count_update = UpdateMessages.objects.filter(user_id=request.user.id).count()
    return render(request, 'event_test.html', {"number": count_update})


def update_message_view(request, user_id=None):
    if request.method == "GET":
        result = {}
        if user_id:
            result['status'] = 'ok'
            result['data'] = {}
            notifications = UpdateMessages.objects.filter(user_id=user_id)
            for notif in notifications:
                result['data'][notif.id] = {"title": notif.title, "description": notif.description}
        else:
            result["status"] = "pleas set user id"
        return JsonResponse(result)
    return render(request, "Salam")
