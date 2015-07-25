from arghandler import *
import unittest

CONTEXT = 'context'
context1_equal = False
context2_equal = False
cmd1_has_run = False
cmd2_has_run = False

@subcmd
def cmd1(context,args):
	global cmd1_has_run, context1_equal

	cmd1_has_run = True
	
	context1_equal = (context == CONTEXT)
	return

@subcmd
def cmd2(context,args):
	global cmd2_has_run, context2_equal
	cmd2_has_run = True

	context2_equal = (context == CONTEXT)
	return

class DecoratorTestCase(unittest.TestCase):

	def test_cmd1(self):

		handler = ArgumentHandler()
		handler.add_argument('-l','--link',action='store_true')
		handler.run(['-l','cmd1'],context_fxn=lambda x: CONTEXT)

		self.assertTrue(cmd1_has_run)

if __name__ == '__main__':
	unittest.main()
