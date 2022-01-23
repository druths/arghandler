# arghandler [![Build Status](https://travis-ci.org/druths/arghandler.svg?branch=master)](https://travis-ci.org/druths/arghandler) #
*Making argparse even more awesome*

I love [argparse](https://docs.python.org/3/library/argparse.html), but there
are some things that it simply doesn't help with as much as I'd like. Enter
arghandler.

The goal behind arghandler is to provide all the capabilities of argparse
*plus* some high-level capabilities that crop up a lot when writing
command-line tools: the library aims for high quality command line interfaces
with (even more) minimal code.

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

	pip install arghandler

or

	easy_install arghandler

You can find arghandler on pypi for relevant details should you need them.

## Usage ##

Just like with
[argparse.ArgumentParser](https://docs.python.org/3/library/argparse.html#argumentparser-objects),
in `arghandler` everything revolves around `ArgumentHandler`. In fact, it's
(not so secretly) a subclass of ArgumentParser, so you can use it exactly the
way you use `ArgumentParser`.  But `ArgumentHandler` has some new tricks.

To benefit from `ArgumentHandler`, your command-line configuration code will
follow this logic:

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

*`ArgumentHandler.run(argv,context_fxn)`* makes the class perform its more
unique and powerful capabilities.  Notably: configuring the logger and running
subcommands.  As with `parse_args(...)`, if `argv` is not specified, then
`sys.argv` will be used.  The `context_fxn` is also optional and is used as
part of subcommand processing.  See that [section](#subcommands) below for more
details.

#### Enabling autocompletion ####

When constructing an `ArgumentHandler`, you can enable autocompletion.  This
requires doing two separate things.

First, pass the keyword argument `enable_autocompetion=True` to
`ArgumentHandler(...)`.

Second, in the top-level script that will be your command-line tool, include
the line

	# PYTHON_ARGCOMPLETE_OK

near the top (in the first 1024 bytes).  For more details on this, see the
[argcomplete](https://argcomplete.readthedocs.io/en/latest/) documentation.

For an example of this in action, see [examples/dummy.py!](examples/dummy.py).

### Setting the logging level ###

If you use the python [logging](https://docs.python.org/3/library/logging.html)
package, this feature will save you some time.

The `ArgumentParser.set_logging_argument(...)` method allows you to specify a
command-line argument that will set the logging level.  The method accepts
several arguments:

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
	def echo(parser,context,args):
		print ' '.join(args)

	# here we associate the subcommand 'foobar' with function cmd_foobar
	@subcmd('foobar', help = 'Does foobar')
	def cmd_foobar(parser,context,args):
		print 'foobar'

	handler = ArgumentHandler()
	handler.run(['echo','hello','world']) # echo will be called and 'hello world' will be printed

Notice that the subcommands always take three arguments.

`args` is the set of arguments that *follow* the subcommand on the command
line.

`context` is an object that can make valuable global information available to
subcommands.  By default, the context is the namespace object returned by the
internal call to `ArgumentHandler.parse_args(...)`.  Other contexts can be
produced by passing a context-producing function to the
`ArgumentHandler.run(...)` function:

	@subcmd('ping')
	def ping_server(parser,server_address,args):
		os.system('ping %s' % server_address)

	handler = ArgumentHandler()
	handler.add_argument('-s','--server')

	# when this is run, the context will be set to the return value of context_fxn
	# in this case, it will be the string '127.0.0.1'
	handler.run(['-s','127.0.0.1','ping'],context_fxn=lambda args: args.server

Finally, `parser` is an instance of `argparse.ArgumentParser` which has been
preconfigured to behave properly for the subcommand.  Most crucially, this
means that `parser.prog` is set to `<top_level_program> <sub_command>` so that
help messages print out correctly for the subcommand.  Should your subcommand
want to parse arguments, this parser object should be used.

### Declaring subcommands without decorators ###

While decorators are the preferred way to specify subcommands, subcommands can
also be specified using the `ArgumentHandler.set_subcommands(...)` function.
This method expects a dictionary: keys are command names, values are the
command functions:

	from arghandler import *

	def echo(parser,context,args):
		print ' '.join(args)

	def cmd_foobar(parser,context,args):
		print 'foobar'

	handler = ArgumentHandler()
	handler.set_subcommands( {'echo':echo, 'foobar':cmd_foobar} )
	handler.run(['echo','hello','world']) # echo will be called and 'hello world' will be printed

All the logic and rules around the context function apply here.  Moreoever, the
complete set of subcommands include those specified using decorators AND those
specified through the `set_subcommands(...)` method.

#### Making subcommands in subcommands ####
One valuable use for the `set_subcommands(...)` method is implementing
subcommand options for a subcommand.  For example, suppose you want a program with the following
command subtree:

```
power
  - create
    - config
    - proj
  - run
    - all
    - proj
```

In this case, `create` and `run` would be top-level subcommands that could be
declared using standard `subcmd` decorators.  But what about the `config` and
`proj` commands underneath `create`?  These can be created using a new
`ArgumentHandler` inside the `create` function like this:

```
def create_config(parser, context, args):
    parser.add_argument('location')
    args = parser.parse_args(args)

    # do stuff

    return

def create_proj(parser, context, args):
    parser.add_argument('name')
    args = parser.parse_args(args)

    print(f'Creating the project: {args.name}')

    # do stuff

    return


@subcmd('create', help='create a resource')
def create(parser, context, args):
    handler = ArgumentHandler()

    handler.set_subcommands({'config': (create_config, 'create a config file'),
                             'proj': (create_proj, 'create a project')
                            },
                            use_registered_subcmds=False)
    
    handler.run(args)
```

Note the use of `use_registered_subcmds=False` - this is important to omit any
functions globally registered as commands using the `@subcmd` decorator.

### Setting the help message ###

The format of the help message can be set to one more friendly for subcommands
by passing the `ArgumentHandler` constructor the keyword argument
`use_subcommand_help=True`.

This will produce a help message that looks something like this:

	usage: test.py [-h] subcommand

	positional arguments:
	  subcommand
        cmd1  cmd1_help_str

	optional arguments:
  	  -h, --help  show this help message and exit

## Some best practices ##

*Use `ArgumentParser` or `ArgumentHandler` inside subcommands.* This will
ensure that informative help messages are available for all your subcommands.

	from arghandler import *

	@subcmd
	def echo(parser,context,args):
		parser.add_argument('-q','--quote_char',required=True)
		args = parser.parse_args(args)
		print '%s%s%s' % (args.quote_char,' '.join(args),args.quote_char)

	@subcmd('foobar')
	def cmd_foobar(parser,context,args):
		print 'foobar'

	handler = ArgumentHandler()
	handler.run(['echo','-h']) # the help message for echo will be printed

*Use logging.* Logging gives you much more control over what
debugging/informational content is printed out by your program. And with
`arghandler` it's easier than ever to configure from the command line!
