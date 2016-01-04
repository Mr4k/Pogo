import sys
class LoadingBar:
	last_text_length = 0
	def __init__(self,outof,begin = "Loading"):
		self.out_of = outof
		self.i = 0
		self.begin = begin
	def print_load(self,increment):
		self.i += increment
		sys.stdout.write("\r"+" "*self.last_text_length)
		prnt = self.begin + " " + str(self.i)+"/"+str(self.out_of)
		sys.stdout.write("\r"+prnt)
		self.last_text_length = len(prnt)
		sys.stdout.flush()
		if self.i >= self.out_of:
			print ""