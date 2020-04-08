from django_signal_notifier.message_templates import get_message_template_from_string

from django.core.management import BaseCommand, CommandError
import importlib


class Command(BaseCommand):
    help = "Call provided test_message_template function and render the specified message_template  .\n" \
           "Example: python manage.py run_message_template myapp.test_dsn.message_template_get_details_function1"

    def add_arguments(self, parser):
        """
        message_template_get_details_functions: The list of functions(message_template run functions) names to be run.
                                (No need to mention 'message_template_get_details_functions'
                                    with run_message_template command)
        debug: Show more details on message_templates running.
                (Use '--debug' option with run_message_template command)
        """
        parser.add_argument('message_template_get_details_functions', nargs='+', type=str,
                            help='Path of the message_template_get_details functions test')
        parser.add_argument('--debug', action='store_true',
                            help='Show more details on the message_template running.')

    def handle(self, *args, **options):
        if 'message_template_get_details_functions' not in options.keys():
            raise CommandError("No message_template run function entered.")

        # Check migrations
        self.check_migrations()

        try:
            for message_template_get_details_function_name in options['message_template_get_details_functions']:
                # Example: message_template_get_details_function_name = "Publish.test_dsn.simple_message_template_run"
                module, function_name = message_template_get_details_function_name.rsplit('.', 1)
                message_template_get_details_function = getattr(importlib.import_module(module), function_name)

                try:
                    message_template_details = message_template_get_details_function()
                except Exception as e:
                    self.stdout.write(f"\nInvalid message_template_get_details_function ({message_template_name}). ")
                    if options['debug']:
                        raise e
                    else:
                        self.stdout.write(f"Use --debug to get more details\n")
                        continue

                self.stdout.write(f"\n######################################################################"
                                  f"\n Rendering message_template based on "
                                  f"{message_template_get_details_function_name} ...\n")

                for message_template_name in message_template_details:
                    try:
                        temp_details = message_template_details[message_template_name]
                        user = temp_details['user']
                        trigger_context = temp_details['trigger_context']
                        signal_kwargs = temp_details['signal_kwargs']
                    except Exception as e:
                        self.stdout.write(f"\nInvalid message_template_get_details_function ({message_template_name}).")
                        if options['debug']:
                            raise e
                        else:
                            self.stdout.write(f"Use --debug to get more details\n")
                            continue

                    message_template_class = get_message_template_from_string(message_template_name)
                    if message_template_class is not None:
                        message_template = message_template_class()
                        # render message_template
                        rendered_message = message_template.render(user, trigger_context, signal_kwargs)
                        self.stdout.write(f"{message_template_name} rendered successfully. Output: \n"
                                          f"{rendered_message}\n")
                    else:
                        self.stdout.write(f'{message_template_name} message_template class '
                                          f'is not registered or renamed.')

        except Exception as e:
            raise e
            # Todo: Unfortunately CommandError can't be run with 'from e' python syntax properly!
            # raise CommandError("Something went wrong on trigger_run_function running ... ") from e
