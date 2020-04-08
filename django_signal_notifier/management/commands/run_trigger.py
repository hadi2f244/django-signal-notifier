from django.core.management import BaseCommand, CommandError
import importlib

from django_signal_notifier.models import Trigger


class Command(BaseCommand):
    help = "Call the corresponding signal of a trigger for testing the DSN flow.\n" \
           "Example: python manage.py run_trigger myapp.test_dsn.trigger_get_details1"

    def add_arguments(self, parser):
        """
        trigger_get_details_function: The list of functions(trigger run functions) names to be run.
                                (No need to mention 'trigger_get_details_functions' with run_trigger command )
        debug: Show more details on triggers running and not matched triggers.
                Not matched trigger with same verb_name are listed in debug mode.
                (Use '--debug' option with run_trigger command)
        """
        parser.add_argument('trigger_get_details_functions', nargs='+', type=str,
                            help='Path of the trigger get_details functions test')
        parser.add_argument('--debug', action='store_true',
                            help='Show more details on the trigger running.')

    def handle(self, *args, **options):
        if 'trigger_get_details_functions' not in options.keys():
            raise CommandError("No trigger get_details function entered.")

        # Check migrations
        self.check_migrations()

        try:
            for trigger_get_details_function_name in options['trigger_get_details_functions']:
                # Example: trigger_get_details_function = "Publish.test_dsn.hello_trigger"
                module, function_name = trigger_get_details_function_name.rsplit('.', 1)
                trigger_get_details_function = getattr(importlib.import_module(module), function_name)

                try:
                    trigger_details = trigger_get_details_function()
                except Exception as e:
                    self.stdout.write(f"\nInvalid trigger_details ({verb_name}). ")
                    if options['debug']:
                        raise e
                    else:
                        self.stdout.write(f"Use --debug to get more details\n")
                        continue

                self.stdout.write(f"\n ######################################################################"
                                  f"\n Running trigger based on {trigger_get_details_function_name} ...\n")
                for verb_name in trigger_details:
                    try:
                        signal_kwargs = trigger_details[verb_name]
                    except Exception as e:
                        self.stdout.write(f"\nInvalid trigger_details ({verb_name}). ")
                        if options['debug']:
                            raise e
                        else:
                            self.stdout.write(f"Use --debug to get more details\n")
                            continue

                    trigger_candidates = Trigger.objects.filter(verb=verb_name)
                    if trigger_candidates.count() == 0:
                        self.stdout.write(f"\nThere is no trigger with '{verb_name}' as verb(signal) name")
                    else:
                        for trigger in trigger_candidates:
                            if trigger.match_signal_trigger(**signal_kwargs):
                                self.stdout.write(f"\nMATCHED trigger is called: {trigger}")
                                trigger.run_corresponding_signal(**signal_kwargs)
                                self.stdout.write(f"{trigger_get_details_function_name} completed successfully."
                                                  f" (Note: You may see output of the backends with delay)")
                            elif options['debug']:
                                self.stdout.write(f"\nNOT MATCHED trigger on signal_kwargs: {trigger}")


        except Exception as e:
            raise e
            # Todo: Unfortunately CommandError can't be run with 'from e' python syntax properly!
            # raise CommandError("Something went wrong on trigger_get_details_function running ... ") from e
