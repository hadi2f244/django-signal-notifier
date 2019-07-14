import sys

class BaseMessanger:
	message = ""
	def send(self):
		print(self.message)
def get_messenger_from_string(str):
	try:
		return getattr(sys.modules[__name__], str)
	except:
		return None


class SimplePrintMessagner1(BaseMessanger):
	message = "Hello, world1!"

class SimplePrintMessagner2(BaseMessanger):
	message = "Hello, world2!"

__messengers_cls_list=[
	SimplePrintMessagner1,
	SimplePrintMessagner2,
]


# register_messengers()
Messengers_name=[(msng.__name__,msng.__name__) for msng in __messengers_cls_list]
