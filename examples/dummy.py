#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK

from arghandler import ArgumentHandler, subcmd

@subcmd('echo', help='echo something')
def echo(parser,context,args):
    print(args)

@subcmd('add', help='add two numbers')
def add(parser,context,args):
    print(sum(args))

if __name__ == '__main__':
    handler = ArgumentHandler(use_subcommand_help=True, enable_autocompletion=True)
    handler.add_argument('-p', help='a test')
    handler.run()
