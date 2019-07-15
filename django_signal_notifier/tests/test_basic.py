from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase,TransactionTestCase

from django_signal_notifier.models import TestModel, Trigger
from django.core.management import call_command

User = get_user_model()


class SignalNotifierTestBase(TransactionTestCase):
	fixtures = ['init_test2.json'] # TODO: action_object_content_type in init_test2.json has some problem!!!

	def setUp(self):
		super(SignalNotifierTestBase, self).setUp()

		Trigger.reconnect_all_triggers()

		self.User = get_user_model()
		# self.testdate = datetime(2000, 1, 1)
		# self.timesince = timesince(self.testdate).encode('utf8').replace(
		#     b'\xc2\xa0', b' ').decode()
		self.group_ct = ContentType.objects.get_for_model(Group)

		self.group1 = Group.objects.create(name='group1')
		self.group2 = Group.objects.create(name='group2')

		self.user1 = self.User.objects.create_superuser('admin', 'admin@test.com', 'admin')
		self.user2 = self.User.objects.create_user('user1', 'user1@test.com')
		self.user3 = self.User.objects.create_user('user2', 'user2@test.com')

		self.user1.groups.add(self.group1)
		self.user1.groups.add(self.group2)
		self.user2.groups.add(self.group1)

		# self.testModel1 = TestModel.objects.create(name='test_model1', extra_field='extra')
		#
		# print(Trigger.objects.all()[0])

	def tearDown(self):
		self.user1.delete()
		self.user2.delete()
		self.user3.delete()
		super(SignalNotifierTestBase, self).tearDown()
