from arghandler import *

@subcmd('cmd1',help='cmd1 help')
def do_cmd1(parser,context,args):
	pass

@subcmd('cmd2')
def do_cmd2(parser,context,args):
	pass


