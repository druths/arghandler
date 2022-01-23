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
import argparse
import logging
import inspect

__all__ = ['ArgumentHandler','LOG_LEVEL','subcmd','reset_registered_subcommands']

LOG_LEVEL = 'log_level'

LOG_LEVEL_STR_LOOKUP = {logging.DEBUG:'DEBUG', logging.INFO:'INFO',
                        logging.WARNING:'WARNING', logging.ERROR:'ERROR',
                        logging.CRITICAL:'CRITICAL'}

def default_log_config(level,args):
    """
    This is the default function used to configure the logging level.
    """
    logging.basicConfig(level=level)

#################################
# decorator
#################################
registered_subcommands = {}
registered_subcommands_help = {}
def subcmd(arg=None, **kwargs):
    """
    This decorator is used to register functions as subcommands with instances
    of ArgumentHandler.
    """
    if inspect.isfunction(arg):
        return subcmd_fxn(arg,arg.__name__, kwargs)
    else:
        def inner_subcmd(fxn):
            return subcmd_fxn(fxn, arg, kwargs)

        return inner_subcmd

def subcmd_fxn(cmd_fxn,name,kwargs):
    global registered_subcommands, registered_subcommands_help

    # get the name of the command
    if name is None:
        name = cmd_fxn.__name__

    registered_subcommands[name] = cmd_fxn
    registered_subcommands_help[name] = kwargs.pop('help','')

    return cmd_fxn

def reset_registered_subcommands():
    """
    Forget about all subcommands that have been registered using @subcmd.
    """
    global registered_subcommands, registered_subcommands_help
    registered_subcommands = {}
    registered_subcommands_help = {}

#########################
# ArgumentHandler class
#########################

class ArgumentHandler(argparse.ArgumentParser):

    def __init__(self,*args,**kwargs):
        """
        All constructor arguments are the same as found in `argparse.ArgumentParser`.

        kwargs
        ------
          * `use_subcommand_help [=True]`: when printing out the help message, use a shortened
            version of the help message that simply shows the sub-commands supported and
            their description.

          * `enable_autocompletion [=False]`: make it so that the command line
            supports autocompletion

        """

        ### extract any special keywords here
        self._use_subcommand_help = kwargs.pop('use_subcommand_help', True)
        self._enable_autocompletion = kwargs.pop('enable_autocompletion', False)

        # some internal logic management info
        self._logging_argument = None
        self._logging_config_fxn = None
        self._ignore_remainder = False
        self._use_subcommands = True
        self._use_registered_subcmds = True
        self._subcommand_lookup = dict()
        self._subcommand_help = dict()

        self._has_parsed = False

        # setup the class
        if self._use_subcommand_help:
            argparse.ArgumentParser.__init__(self,formatter_class=argparse.RawTextHelpFormatter,*args,**kwargs)
        else:
            argparse.ArgumentParser.__init__(self,*args,**kwargs)

    def ignore_subcommands(self):
        """
        Force this ArgumentHandler to not handle any subcommands it might find or be given.
        """
        self._use_subcommands = False

    def set_logging_argument(self, *names, **kwargs): 
        """
        Enable and set an optional argument for setting the logging level that will be
        used by the built-in logging framework.

          * `names` is the set of positional arguments that will set the logging
            level.

          * `default_level` is the default logging level that will be set

          * `config_fxn` allows special handling of the logger config.
            Otherwise, basicConfig will be used. The config function should
            accept two arguments - the first the logging level, the second the
            full set of arguments past to the command.

        """
        # get the keyword args
        default_level = kwargs.pop('default_level',logging.ERROR)
        config_fxn = kwargs.pop('config_fxn',default_log_config)

        if len(kwargs) > 0:
            raise ValueError('unexpected keyword arguments: %s' % ','.join(kwargs.keys()))

        # check the names
        longest_name = ''
        for name in names:
            if not name.startswith('-'):
                raise ValueError('all logging level argument names must start with a "-"')

            oname = name.replace('-','')
            if len(oname) > len(longest_name):
                longest_name = oname

        self._logging_argument = longest_name

        # covert default logging level to a string
        if default_level not in LOG_LEVEL_STR_LOOKUP:
            raise ValueError('the default logging level must be a valid logging level')

        default_level = LOG_LEVEL_STR_LOOKUP[default_level]

        self._logging_config_fxn = config_fxn

        self.add_argument(*names,choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'],
                          default=default_level)

        return

    def add_argument(self,*args,**kwargs):
        """
        This has the same functionality as `argparse.ArgumentParser.add_argument`.
        """
        # just watch for the REMAINDER nargs to see if subcommands are relevant

        if self._ignore_remainder and 'nargs' in kwargs and kwargs['nargs'] == argparse.REMAINDER:
            self._use_subcommands = False

        return argparse.ArgumentParser.add_argument(self,*args,**kwargs)

    def set_subcommands(self, subcommand_lookup, use_registered_subcmds=True):
        """
        Provide a set of subcommands that this instance of ArgumentHandler should
        support.  This is an alternative to using the decorator `@subcmd`. 

        By default, the total set of subcommands supported will be those
        specified in this method combined with those identified by the
        decorator. To ignore all commands identified by decorator, set
        `use_registered_subcmds` to `False`.  This is a desired behavior when
        using this command, for example, as part of a subcommand.
        """
        if type(subcommand_lookup) is not dict:
            raise TypeError('subcommands must be specified as a dict')

        # sanity check the subcommands
        self._subcommand_lookup = {}
        self._subcommand_help = {}
        for cn,cf in subcommand_lookup.items():
            if type(cn) is not str:
                raise TypeError('subcommand keys must be strings. Found %s' % str(cn))
            if type(cf) == tuple:
                if not callable(cf[0]):
                    raise TypeError('subcommand with name %s must be callable' % cn)
                else:
                    self._subcommand_lookup[cn] = cf[0]
                    self._subcommand_help[cn] = cf[1]
            elif not callable(cf):
                raise TypeError('subcommand with name %s must be callable' % cn)
            else:
                self._subcommand_lookup[cn] = cf
                self._subcommand_help[cn] = ''

        self._use_registered_subcmds = use_registered_subcmds
        return

    def parse_args(self,argv=None):
        """
        Works the same as `argparse.ArgumentParser.parse_args`.
        """
        global registered_subcommands, registered_subcommands_help

        if self._has_parsed:
            raise Exception('ArgumentHandler.parse_args can only be called once')

        # collect registered subcommands into _subcommand_lookup
        if self._use_registered_subcmds:
            for cn,cf in registered_subcommands.items():
                self._subcommand_lookup[cn] = cf
                self._subcommand_help[cn] = registered_subcommands_help[cn]

        if len(self._subcommand_lookup) == 0:
            self._use_subcommands = False

        # add in subcommands if appropriate
        if not self._use_subcommands:
            pass
        else:
            max_cmd_length = max([len(x) for x in self._subcommand_lookup.keys()])
            subcommands_help_text = 'the subcommand to run'
            if self._use_subcommand_help:
                subcommands_help_text = '\n'
                for command in sorted(self._subcommand_lookup.keys()):
                    subcommands_help_text += command.ljust(max_cmd_length+2)
                    subcommands_help_text += self._subcommand_help[command]
                    subcommands_help_text += '\n'
            self.add_argument('cmd',choices=self._subcommand_lookup.keys(),help=subcommands_help_text,metavar='subcommand')

            cargs_help_msg = 'arguments for the subcommand' if not self._use_subcommand_help else argparse.SUPPRESS
            self.add_argument('cargs',nargs=argparse.REMAINDER,help=cargs_help_msg)

        # handle autocompletion if requested
        if self._enable_autocompletion:
            import argcomplete
            argcomplete.autocomplete(self)

        # parse arguments
        args = argparse.ArgumentParser.parse_args(self,argv)
        self._has_parse = True

        return args

    def run(self,argv=None,context_fxn=None):
        """
        This method triggers a three step process:

          1) Parse the arguments in `argv`. If not specified, `sys.argv` is
             used.

          2) Configure the logging level.  This only happens if the
             `set_logging_argument` was called.

          3) Run the appropriate subcommand.  This only happens if subcommands
             are available and enabled. Prior to the subcommand being run,
             the `context_fxn` is called.  This function accepts one argument -
             the namespace returned by a call to `parse_args`.

        The parsed arguments are all returned.
        """
        # get the arguments
        args = self.parse_args(argv)

        # handle the logging argument
        if self._logging_argument:
            level = eval('args.%s' % self._logging_argument)

            # convert the level
            level = eval('logging.%s' % level)

            # call the logging config fxn
            self._logging_config_fxn(level,args)

        # generate the context
        context = args
        if context_fxn:
            context = context_fxn(args)

        if self._use_subcommands:
            # create the sub command argument parser
            scmd_parser = argparse.ArgumentParser(prog='%s %s' % (self.prog,args.cmd))

            # handle the subcommands
            self._subcommand_lookup[args.cmd](scmd_parser,context,args.cargs)

        return args
