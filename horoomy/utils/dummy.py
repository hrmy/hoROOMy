
class Dummy():

	def __call__(self, *args, **kwargs):
		return self

	def __getattr__(self, *args, **kwargs):
		return self

	def __getitem__(self, *args, **kwargs):
		return self

	def __setitem__(self, *args, **kwargs):
		return self