import unittest
from arghandler import *

class SubCmdTestCase(unittest.TestCase):
    
    def test_use_subcmd(self):
        reset_registered_subcommands()
        import arghandler.tests.subcmds1

    def test_reported(self):
        reset_registered_subcommands()

        @subcmd('foobar', help='Does foobar')
        def cmd_foobar(parser, context, args):
            pass

        handler = ArgumentHandler()
        handler.run(['foobar','hello','world'])
