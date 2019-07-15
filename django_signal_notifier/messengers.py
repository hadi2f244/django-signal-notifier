import sys

class BaseMessenger:
	message = ""
	def send(self):
		print(self.message)
def get_messenger_from_string(str):
	try:
		return getattr(sys.modules[__name__], str)
	except:
		return None


class SimplePrintMessenger1(BaseMessenger):
	message = "Hello, world1!"

class SimplePrintMessenger2(BaseMessenger):
	message = "Hello, world2!"

__messengers_cls_list=[
	SimplePrintMessenger1,
	SimplePrintMessenger2,
]


# register_messengers()
Messengers_name=[(msng.__name__,msng.__name__) for msng in __messengers_cls_list]
