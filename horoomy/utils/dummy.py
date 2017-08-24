
class Dummy():

	def __call__(self, method):
		return self

	def __getattr__(self, name):
		return self

	def __getitem__(self, index):
		return self

	def __setitem__(self, index, value):
		return self