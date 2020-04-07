from django.core.management import BaseCommand, CommandError
import importlib

from django_signal_notifier.models import Trigger


class Command(BaseCommand):
    help = "Call the corresponding signal of a trigger for testing the DSN flow.\n" \
           "Example: python manage.py run_trigger myapp.test_trigger.trigger_run_function1"

    def add_arguments(self, parser):
        """
        trigger_run_functions: The list of functions(trigger run functions) names to be run.
                                (No need to mention 'trigger_run_functions' with run_trigger command )
        debug: Show more details on triggers running and not matched triggers.
                (Use '--debug' option with run_trigger command)
        """
        parser.add_argument('trigger_run_functions', nargs='+', type=str,
                            help='Path of the trigger functions test')
        parser.add_argument('--debug', action='store_true',
                            help='Show more details on the trigger running.')

    def handle(self, *args, **options):
        if 'trigger_run_functions' not in options.keys():
            raise CommandError("No trigger run function entered.")

        # Check migrations
        self.check_migrations()

        try:
            for trigger_run_function_name in options['trigger_run_functions']:
                # Example: trigger_run_function_name = "Publish.test_trigger.hello_trigger"
                module, function_name = trigger_run_function_name.rsplit('.', 1)
                trigger_run_function = getattr(importlib.import_module(module), function_name)

                trigger_details = trigger_run_function()

                self.stdout.write(f"\n ######################################################################"
                                  f"\n Running {trigger_run_function_name} ...\n")
                for verb_name in trigger_details:
                    signal_kwargs = trigger_details[verb_name]
                    trigger_candidates = Trigger.objects.filter(verb=verb_name)
                    if trigger_candidates.count() == 0:
                        self.stdout.write(f"\nThere is no trigger with '{verb_name}' as verb(signal) name")
                    else:
                        for trigger in trigger_candidates:
                            if trigger.match_signal_trigger(**signal_kwargs):
                                self.stdout.write(f"\nMATCHED trigger is called: {trigger}")
                                trigger.run_corresponding_signal(**signal_kwargs)
                            elif options['debug']:
                                self.stdout.write(f"\nNOT MATCHED trigger on signal_kwargs: {trigger}")
                        self.stdout.write(f"{trigger_run_function_name} completed successfully."
                                          f" (Note: You may see output of the backends with delay)")

        except Exception as e:
            raise e
            # Todo: Unfortunately CommandError can't be run with 'from e' python syntax properly!
            # raise CommandError("Something went wrong on trigger_run_function running ... ") from e
