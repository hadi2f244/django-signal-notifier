from django.shortcuts import render

from Publish.models import Book


def index1(request):
    obj = Book.objects.all()
    return render(request, "index.html", locals())

def index2(request):
    obj = Book.objects.all().select_related("publisher")
    return render(request, "index.html", locals())

def index3(request):
    obj = Book.objects.all().prefetch_related("publisher")
    return render(request, "index.html", locals())