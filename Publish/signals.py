from django.dispatch import Signal

book_published = Signal(providing_args=["instance"])
