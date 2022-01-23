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
import sys
import unittest
import logging
import argparse
from arghandler import *

import multiprocessing

class LoggingTestCase(unittest.TestCase):

    def test_default_config(self):
        reset_registered_subcommands()

        handler = ArgumentHandler()
        handler.set_logging_argument('-L','--logging')

        handler.run(['-L','ERROR'])

        logger = logging.getLogger()
        self.assertEqual(logger.level,logging.ERROR)
        
class SubcommandHelpTestCase(unittest.TestCase):
    
    def test_subcommand_text(self):
        reset_registered_subcommands()

        def do_test(handler,args):
            original_stdout = sys.stdout
            sys.stdout = open('/tmp/short_text.out','w')
            original_stderr = sys.stderr
            sys.stderr = open('/tmp/short_text.err','w')
        
            handler.run(args)

            sys.stdout.close()
            sys.stdout = original_stdout
            sys.stderr.close()
            sys.stderr = original_stderr
        
        def cmd1(parser,context,args):
            pass

        handler = ArgumentHandler(use_subcommand_help=True)
        handler.set_subcommands({'cmd1':(cmd1,'cmd1_help_str')})

        p = multiprocessing.Process(target=do_test,args=(handler,['-h']))
        p.start()
        p.join()


        # check for the cmd1 help message
        out_contents = open('/tmp/short_text.out','r').read()
        err_contents = open('/tmp/short_text.err','r').read()

        self.assertTrue('cmd1_help_str' in out_contents)

class ContextTestCase(unittest.TestCase):

    def test_default_context(self):
        reset_registered_subcommands()
        
        self.cmd1_has_run = False

        def cmd1(parser,context,args):
            self.cmd1_has_run = True
            self.assertEqual(type(parser),argparse.ArgumentParser)
            self.assertTrue(context.link)
            self.assertEqual(context.arg2,'foobar')

        handler = ArgumentHandler()
        handler.set_subcommands({'cmd1':cmd1})
        handler.add_argument('-l','--link',action='store_true')
        handler.add_argument('arg2')

        handler.run(['-l','foobar','cmd1'])

        self.assertTrue(self.cmd1_has_run)

    def test_run_testcase(self):
        reset_registered_subcommands()

        self.context_has_run = False
        self.cmd_has_run = False
        self.CONTEXT = 'context'

        def cmd1(parser,context,args):
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

class ExplicitSubCommandTestCase(unittest.TestCase):

    def test_no_registered(self):
        reset_registered_subcommands()

        @subcmd
        def my_cmd(parser, context, args):
            pass

        def my_cmd2(parser, context, args):
            pass

        handler = ArgumentHandler()
        handler.set_subcommands({'cmd2': (my_cmd2, 'help')}, use_registered_subcmds=False)

        handler.parse_args(['cmd2'])

        self.assertEqual(len(handler._subcommand_lookup), 1)
        self.assertTrue('cmd2' in handler._subcommand_lookup)
