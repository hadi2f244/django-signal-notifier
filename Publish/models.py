from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=30, verbose_name="Name")
    address = models.CharField("address", max_length=50)
    city = models.CharField('City', max_length=60)
    state_province = models.CharField(max_length=30)
    country = models.CharField(max_length=50)
    website = models.URLField()

    class Meta:
        verbose_name = 'Publisher'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=30)
    hobby = models.CharField(max_length=20, default="", blank=True, null=True)
    hobby2 = models.CharField(max_length=20, blank=True, null=True)
    hobby3 = models.CharField(max_length=20, default="", blank=True, null=True)
    hobby1 = models.CharField(max_length=20, default="", blank=True)



    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name="Title")
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, verbose_name="Press")
    publication_date = models.DateField(null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=10, verbose_name="Price")

    def __str__(self):
        return self.title