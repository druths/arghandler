# arghandler #
*Making argparse even more awesome*

We love [argparse](https://docs.python.org/3/library/argparse.html), but there
are some things that it simply doesn't help with as much as we'd like. Enter
arghandler.

The goal behind arghandler is to provide all the capabilities of argparse
*plus* some high-level capabilities that crop up a lot when writing
command-line tools.  The goal here is high quality command line interfaces with
minimal code.

At present, arghandler provides two key capabilities:

  1. Adding subcommands with basically zero extra lines of code. This gives
  support for writing programs like `git` and `svn` which have nested
  subcommands.

  1. Configuring the logging framework (e.g., the desired logging level) from
  the command line - again with basically one line of code.

We have lots more improvements we want to add - and as we have time and receive
feedback, we'll add more features.

If you have ideas, [email me](mailto:druths@networkdynamics.org) or code it up
and generate a pull request!

## Installation ##

Use `pip` or `easy_install` to install the library:

	pip install argparse

or 

	easy_install argparse

You can find argparse on [pypi](http://TODO) for relevant details should you need them.

## Usage ##

Just like with
[argparse.ArgumentParser](https://docs.python.org/3/library/argparse.html#argumentparser-objects),
in `arghandler` everything revolves around `ArgumentHandler`. In fact, it's
(not so secretly) a subclass of ArgumentParser, so you can use it exactly the
way you use `ArgumentParser`.  But `ArgumentHandler` has some new tricks.

To benefit from `ArgumentHandler`, your command-line configuration code will follow this logic:

	from arghandler import ArgumentHandler

	handler = ArgumentHandler() # this accepts all args supported by ArgumentParser

	# config the handler using add_argument, set_logging_level, set_subcommands, etc...

	handler.run() # throw the configured handler at an argument string!

Now for some details...

### Invoking ArgumentHandler ###

`ArgumentHandler` can be invoked on arguments in two ways.  

*`ArgumentHandler.parse_args([argv])`* is little different from
`ArgumentParser.parse_args([argv])`.  If `argv` is omitted, then the value of
`sys.argv` is used. The only notable differences are:

  * If a logging argument was set, then this will be included in the namespace
    object returned.

  * If subcommands are available, then the subcommand will be given by the
	value of `args.cmd` and the subcommand's arguments will be given by
	`args.cargs`.

*`ArgumentHandler.run(argv,context_fxn)`* makes the class perform its more unique and powerful capabilities.  Notably: configuring the logger and running subcommands.  As with `parse_args(...)`, if `argv` is not specified, then `sys.argv` will be used.  The `context_fxn` is also optional and is used as part of subcommand processing.  See that [section](#subcommands) below for more details.

### Setting the logging level ###

If you use the python [logging](https://docs.python.org/3/library/logging.html) package, this feature will save you some time.

The `ArgumentParser.set_logging_argument(...)` method allows you to specify a command-line argument that will set the logging level.  The method accepts several arguments:

	ArgumentParser.set_logging_argument(*names,default_level=logging.ERROR,config_fxn=None)


  * `*names` stands in for one or more arguments that specify the 
	argument names that will be used. These follow the same rules as ones
	passed into
	[ArgumentParser.add_argument(...)](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument).
	Moreover, they MUST be optional arguments (i.e., start with a '-'
	character).

  * `default_level` indicates the default level the logging 
	framework will be set to should the level not be specified on the command
	line.

  * `config_fxn` allows the developer to write special logging 
	configuration code.  If not specified, the
	[logging.basicConfig](https://docs.python.org/3/library/logging.html#logging.basicConfig)
	function will be invoked with the appropriate logging level. The function
	must accept two arguments: the logging level and the namespace args object
	returned by the `ArgumentParser.parse_args` method. The configuration
	itself will happen when the `ArgumentHandler.run(...)` method is called.

If you're cool with the defaults in `basicConfig`, then your method call will
look something like this

	handler.set_logging_argument('-l','-log_level',default_level=logging.INFO)

If you do want to do some customization, then your code will look like this

	handler.set_logging_argument('-l','-llevel',
		config_fxn=lambda level,args: logging.basicConfig(level=level,format='%(message)'))

### <a name="subcommands"></a>Declaring subcommands using decorators ###

This feature makes it possible to write nested commands like `git commit` and
`svn checkout` with basically zero boilerplate code.  To do this `arghandler`
provides the `@subcmd` decorator.  To declare a subcommand, just put the
decorator on the function  you want to act as the subcommand.

	from arghandler import *

	@subcmd
	def echo(context,args):
		print ' '.join(args)
	
	# here we associate the subcommand 'foobar' with function cmd_foobar
	@subcmd('foobar')
	def cmd_foobar(context,args):
		print 'foobar'

	handler = ArgumentHandler()
	handler.run(['echo','hello','world']) # echo will be called and 'hello world' will be printed

Notice that the subcommands always take two arguments. `args` is the set of
arguments that *follow* the subcommand on the command line. `context` is an
object that can make valuable global information available to subcommands.  By
default, the context is the namespace object returned by the internal call to
`ArgumentHandler.parse_args(...)`.  Other contexts can be produced by passing a
context-producing function to the `ArgumentHandler.run(...)` function:

	@subcmd('ping')
	def ping_server(server_address,args):
		os.system('ping %s' % server_address)

	handler = ArgumentHandler()
	handler.add_argument('-s','--server')

	# when this is run, the context will be set to the return value of context_fxn
	# in this case, it will be the string '127.0.0.1'
	handler.run(['-s','127.0.0.1','ping'],context_fxn=lambda args: args.server

### Declaring subcommands without decorators ###

While decorators are the preferred way to specify subcommands, subcommands can also be specified using the `ArgumentHandler.set_subcommands(...)` function.  This method expects a dictionary: keys are command names, values are the command functions:

	from arghandler import *

	def echo(context,args):
		print ' '.join(args)
	
	def cmd_foobar(context,args):
		print 'foobar'

	handler = ArgumentHandler()
	handler.set_subcommands( {'echo':echo, 'foobar':cmd_foobar} )
	handler.run(['echo','hello','world']) # echo will be called and 'hello world' will be printed

All the logic and rules around the context function apply here.  Moreoever, the
complete set of subcommands include those specified using decorators AND those
specified through the `set_subcommands(...)` method.

## Some best practices ##

*Use `ArgumentParser` or `ArgumentHandler` inside subcommands.* This will
ensure that informative help messages are available for all your subcommands.

	from arghandler import *

	@subcmd
	def echo(context,args):
		handler = ArgumentHandler()
		handler.ignore_subcommands()
		handler.add_argument('-q','--quote_char',required=True)
		args = handler.parse_args(args)
		print '%s%s%s' % (args.quote_char,' '.join(args),args.quote_char)
	
	@subcmd('foobar')
	def cmd_foobar(context,args):
		print 'foobar'

	handler = ArgumentHandler()
	handler.run(['echo','-h']) # the help message for echo will be printed

*Use logging.* Logging gives you much more control over what
debugging/informational content is printed out by your program. And with
`arghandler` it's easier than ever to configure from the command line!


