import unittest
import logging
from arghandler import *

class LoggingTestCase(unittest.TestCase):

	def test_default_config(self):
		handler = ArgumentHandler()
		handler.set_logging_argument('-L','--logging')

		handler.run(['-L','ERROR'])

		logger = logging.getLogger()
		self.assertEquals(logger.level,logging.ERROR)
		
class ContextTestCase(unittest.TestCase):

	def test_default_context(self):
		self.cmd1_has_run = False

		def cmd1(context,args):
			self.cmd1_has_run = True
			self.assertTrue(context.link)
			self.assertEquals(context.arg2,'foobar')

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
			self.assertEquals(context,self.CONTEXT)
			self.assertEquals(args[0],'foobar')

		def context_fxn(args):
			self.context_has_run = True

			self.assertEquals(args.a1,'hello')
			self.assertEquals(args.a2,'there')

			return self.CONTEXT

		cmds = {'cmd1':cmd1}

		handler = ArgumentHandler()
		handler.set_subcommands(cmds)
		handler.add_argument('a1')
		handler.add_argument('a2')
		handler.run(['hello','there','cmd1','foobar'],context_fxn)

		self.assertTrue(self.context_has_run)
		self.assertTrue(self.cmd_has_run)
