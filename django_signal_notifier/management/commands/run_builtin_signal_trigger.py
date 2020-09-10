from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from django_signal_notifier.exceptions import ContentTypeObjectDoesNotExist
from django_signal_notifier.models import django_default_signal_list, Trigger


class Command(BaseCommand):
    help = "Call the corresponding signal (Django builtin signals) of a trigger for testing the DSN flow. " \
           "This command is interactive."

    def get_signal_details_interactive(self, trigger_id=None):
        """
        Get specification of the trigger (verb_name, action_object, ...) by user input
        :return: trigger
        """

        # 1. Get trigger
        verb_name = ""
        trigger = None
        if trigger_id is not None:
            try:
                trigger = Trigger.objects.get(id=trigger_id)
                verb_name = trigger.verb
            except ObjectDoesNotExist:
                self.stdout.write(f"\nThere is no trigger in DB with id equals {trigger_id}:\n")
                return None
        else:  # trigger_id is not specified
            # 1. Get verb_name
            self.stdout.write("\nSelect verb_name(signal name):\n")
            for i, verb_name in enumerate(django_default_signal_list+['All triggers']):
                self.stdout.write(f"{i} ::: {verb_name}\n")

            while 1:
                temp_input = input("Select the verb_name or the line number: ").strip()
                try:
                    select_index = int(temp_input)
                    if select_index == len(django_default_signal_list):  # All triggers item is selected
                        verb_name = None
                        break
                    else:
                        try:
                            verb_name = django_default_signal_list[select_index]
                            break
                        except (IndexError, AssertionError):
                            self.stdout.write("Invalid number!\n")
                            continue
                except ValueError:
                    if temp_input in django_default_signal_list:
                        verb_name = temp_input
                    else:
                        self.stdout.write("\nInvalid verb_name!\n")
                        continue

            # 2. Show the candidate triggers
            if verb_name is None: # All triggers item is selected
                trigger_candidates = Trigger.objects.all()
            else:
                trigger_candidates = Trigger.objects.filter(verb=verb_name)

            if trigger_candidates.count() == 0:
                self.stdout.write(f"\nThere is no trigger with '{verb_name}' as verb(signal) name")
                return None

            self.stdout.write("\nSelect the trigger:\n")
            for i, trigger in enumerate(trigger_candidates):
                self.stdout.write(f"{i} ::: {trigger}\n")

            while 1:
                temp_input = input("Select the line number: ").strip()
                try:
                    select_index = int(temp_input)
                    trigger = trigger_candidates[select_index]
                    break
                except (ValueError, IndexError, AssertionError):
                    self.stdout.write("Invalid number!\n")
                    continue
            self.stdout.write(f"Selected trigger ::: {trigger}\n")

        # 2. Obtain Trigger details
        sender = None
        instance = None
        if trigger.action_object_content_type is not None:
            sender = trigger.action_object_content_type.model_class()
            if trigger.action_object_id is not None:
                try:
                    instance = trigger.action_object_content_type.model_class().objects.get(
                        pk=int(trigger.action_object_id))
                except ObjectDoesNotExist as e:
                    self.stdout.write(f"Improper trigger : The action_object has been deleted.\n")
                    raise ContentTypeObjectDoesNotExist(
                        f"Can't find any object (action_object) with this id equals {trigger.action_object_id} "
                        f"for {trigger.action_object_content_type.model_class()}") from e
            else:
                self.stdout.write(f"\nAction_object(instance) value is not specified.")
                while 1:
                    temp_input = input(
                        f"Enter an id to select the object of {sender} for 'instance' value of the signal"
                        f"(To select first object of the model in db, leave this field empty): ").strip()
                    if temp_input == "":
                        temp_input = "1"
                    try:
                        select_id = int(temp_input)
                        try:
                            instance = trigger.action_object_content_type.model_class().objects.get(
                                pk=int(select_id))
                            break
                        except ObjectDoesNotExist:
                            self.stdout.write(
                                f"Can't obtain {sender} model with this {select_id} as id, "
                                "It may be deleted. \n Note: There must be at least one item of this model in DB")
                            continue
                    except IndexError:
                        self.stdout.write("\nInvalid number!\n")
                        continue

        self.stdout.write(f"\nAction_object model(sender) is {sender}.")
        self.stdout.write(f"\nAction_object (instance) is {instance}.")

        # Check actor_object
        actor_object = None
        if trigger.actor_object_content_type is not None:
            actor_object = trigger.actor_object_content_type.model_class()
            if trigger.actor_object_id is not None:
                try:
                    actor_object = trigger.actor_object_content_type.model_class().objects.get(
                        pk=int(trigger.actor_object_id))
                except ObjectDoesNotExist as e:
                    self.stdout.write(f"Improper trigger : The actor_object has been deleted.\n")
                    raise ContentTypeObjectDoesNotExist(
                        f"Can't find any object (actor_object) with this id equals {trigger.actor_object_id} "
                        f"for {trigger.actor_object_content_type.model_class()}") from e

        self.stdout.write(f"\nActor_object model(sender) is {actor_object}.")

        target = trigger.target

        return {
            'trigger': trigger,
            'verb_name': verb_name,
            'sender': sender,
            'instance': instance,
            'actor_object': actor_object,
            'target': target,
        }

    def add_arguments(self, parser):
        """
        trigger_id: Id of of the trigger in DB.
                (Use '--trigger_id' option with run_builtin_signal_trigger command)
        """
        parser.add_argument('--trigger_id', type=int,  # Default value is 'None'
                            help='Id of of the trigger in DB')

    def handle(self, *args, **options):
        trigger_details = self.get_signal_details_interactive(trigger_id=options['trigger_id'])
        if trigger_details is None:
            return

        self.check_migrations()

        signal_kwargs = {
            'sender': trigger_details['sender'],  # action_object
            'instance': trigger_details['instance'],
            'actor_object': trigger_details['actor_object'],
            'target': trigger_details['target']
        }

        verb_signal = trigger_details['trigger'].get_verb_signal()
        for arg in verb_signal.providing_args:
            if arg not in signal_kwargs.keys():
                signal_kwargs[arg] = None

        # Note: It is not proper to just provide sender, instance and trigger specification, Some signals need more than this.
        # run corresponding signal
        self.stdout.write(f"\n{trigger_details['verb_name']} signal called by \n {signal_kwargs} "
                          f"\n as signal_kwargs \n")
        self.stdout.write("\nWait for the backends to be run ... \n")
        trigger_details['trigger'].run_corresponding_signal(**signal_kwargs)

        self.stdout.write("\nNote: Standard signal parameters(sender, instance) are set as you enter while "
                          "other parameters(like providing_args of the signal) filled with 'None'. \n"
                          "Though it is better to use 'run_trigger' command with customized and "
                          "proper signal parameters manually. \n\n")
