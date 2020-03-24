from django.core.management import BaseCommand, CommandError
import importlib


class Command(BaseCommand):
    help = "Call the corresponding signal of a trigger for testing the DSN flow.####"

    def handle(self, *args, **options):
        self.stdout.write("testing DSN")



        mod = importlib.import_module("Publish.test_trigger")

        mod.hello_trigger()
        try:
            pass
        except:
            raise CommandError("Something went wrong.")