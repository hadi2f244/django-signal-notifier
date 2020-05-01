from django.core.management import BaseCommand, CommandError
import importlib


class Command(BaseCommand):
    help = "A command to run test_send() function of backends\n" \
           "Example: python manage.py test_messenger" \
           " django_signal_notifier.messengers.SimplePrintMessenger user1 'test_message_text'"

    def add_arguments(self, parser):
        """
        parameters: Contains 3 parameters: (No need to mention 'parameters' with test_messenger command )
            - name of messenger class.
            - user_identification
            - test_message
        """
        parser.add_argument('parameters', nargs='+', type=str,
                            help='Path of the messenger class')

    def handle(self, *args, **options):
        if 'parameters' not in options.keys():
            raise CommandError("No messenger entered.")

        if len(options['parameters']) != 3:
            raise CommandError("Format of test_messenger parameters must like below:\n"
                               "    test_messenger <module_path.messenger_class> <user_identification> <test_message>\n"
                               "    test_messenger <module_path.messenger_class> "
                               "<user_identification> '<long test_message>' \n")


        messenger_path, user_identification, test_message = options['parameters']

        try:
            module, messenger_name = messenger_path.rsplit('.', 1)
            messenger = getattr(importlib.import_module(module), messenger_name)
        except Exception as e:
            raise e

        # Run test_send
        self.stdout.write(f"\n ######################################################################"
                          f"\n Running {messenger} ...\n")
        messenger.test_send(user_identification=user_identification, test_message=test_message)
