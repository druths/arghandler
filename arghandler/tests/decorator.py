"""
Copyright 2015 Derek Ruths

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
