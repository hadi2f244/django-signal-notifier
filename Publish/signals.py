from django.dispatch import Signal

book_published = Signal(providing_args=["instance", "who"])
book_pre_published = Signal(providing_args=["instance"])