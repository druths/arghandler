#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK

from arghandler import ArgumentHandler, subcmd

@subcmd('echo')
def echo(parser,context,args):
	print args	

@subcmd('add')
def add(parser,context,args):
	print sum(args)

if __name__ == '__main__':
	handler = ArgumentHandler(enable_autocompletion=True)
	handler.run()
