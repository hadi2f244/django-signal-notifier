from django.contrib import admin

# Register your models here.
from Publish import models

admin.site.register(models.Book)
admin.site.register(models.Author)
admin.site.register(models.Publisher)
