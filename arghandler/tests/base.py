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

import unittest
import logging
from arghandler import *

class LoggingTestCase(unittest.TestCase):

	def test_default_config(self):
		handler = ArgumentHandler()
		handler.set_logging_argument('-L','--logging')

		handler.run(['-L','ERROR'])

		logger = logging.getLogger()
		self.assertEqual(logger.level,logging.ERROR)
		
class ContextTestCase(unittest.TestCase):

	def test_default_context(self):
		self.cmd1_has_run = False

		def cmd1(context,args):
			self.cmd1_has_run = True
			self.assertTrue(context.link)
			self.assertEqual(context.arg2,'foobar')

		handler = ArgumentHandler()
		handler.set_subcommands({'cmd1':cmd1})
		handler.add_argument('-l','--link',action='store_true')
		handler.add_argument('arg2')

		handler.run(['-l','foobar','cmd1'])

		self.assertTrue(self.cmd1_has_run)

	def test_run_testcase(self):
		self.context_has_run = False
		self.cmd_has_run = False
		self.CONTEXT = 'context'

		def cmd1(context,args):
			self.cmd_has_run = True
			self.assertEqual(context,self.CONTEXT)
			self.assertEqual(args[0],'foobar')

		def context_fxn(args):
			self.context_has_run = True

			self.assertEqual(args.a1,'hello')
			self.assertEqual(args.a2,'there')

			return self.CONTEXT

		cmds = {'cmd1':cmd1}

		handler = ArgumentHandler()
		handler.set_subcommands(cmds)
		handler.add_argument('a1')
		handler.add_argument('a2')
		handler.run(['hello','there','cmd1','foobar'],context_fxn)

		self.assertTrue(self.context_has_run)
		self.assertTrue(self.cmd_has_run)
