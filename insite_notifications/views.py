from django.shortcuts import render
from django_eventstream import send_event


def test_notifications(request):
    return render(request, 'event_test.html')
