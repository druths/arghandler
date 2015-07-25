import sys
import argparse
import logging

__all__ = ['ArgumentHandler','LOG_LEVEL','subcmd']

LOG_LEVEL='log_level'

LOG_LEVEL_STR_LOOKUP = { logging.DEBUG:'DEBUG', logging.INFO:'INFO',
						logging.WARNING:'WARNING', logging.ERROR:'ERROR',
						logging.CRITICAL:'CRITICAL' }

def default_log_config(level,args):
	logging.basicConfig(level=level)

# decorator
registered_subcommands = {}
def subcmd(cmd_fxn,name=None):
	global registered_subcommands
	
	# get the name of the command
	if name is None:
		name = cmd_fxn.__name__
	
	registered_subcommands[name] = cmd_fxn

	return cmd_fxn

class ArgumentHandler(argparse.ArgumentParser):

	def __init__(self,*args,**kwargs):

		### extract any special keywords here
		# None to extract...

		# some internal logic management info
		self._logging_argument = None
		self._logging_config_fxn = None
		self._ignore_remainder = False
		self._use_subcommands = True
		self._subcommand_lookup = dict()

		self._has_parsed = False

		# setup the class
		argparse.ArgumentParser.__init__(self,*args,**kwargs)

	def ignore_subcommands(self):
		"""
		Force this ArgumentHandler to not handle any subcommands it might find or be given.
		"""
		self._use_subcommands = False

	def set_logging_argument(self,*names,**kwargs): #,default_level=logging.ERROR,config_fxn=None):
		"""
		names is the set of positional arguments that will set the logging
		level.

		default_level is the default logging level that will be set

		config_fxn allows special handling of the logger config.  otherwise,
		basicConfig will be used.
		"""
		# get the keyword args
		default_level = kwargs.pop('default_value',logging.ERROR)
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
		# just watch for the REMAINDER nargs to see if subcommands are relevant

		if self._ignore_remainder and 'nargs' in kwargs and kwargs['nargs'] == argparse.REMAINDER:
			self._use_subcommands = False

		return argparse.ArgumentParser.add_argument(self,*args,**kwargs)

	def set_subcommands(self,subcommand_lookup):
		
		if type(subcommand_lookup) is not dict:
			raise TypeError('subcommands must be specified as a dict')

		# sanity check the subcommands
		for cn,cf in subcommand_lookup.items():
			if type(cn) is not str:
				raise TypeError('subcommand keys must be strings. Found %s' % str(cn))
			if not callable(cf):
				raise TypeError('subcommand with name %s must be callable' % cn)

		# store the subcommands
		self._subcommand_lookup = dict(subcommand_lookup)

		return

	def parse_args(self,argv=None):	
		global registered_subcommands

		if self._has_parsed:
			raise Exception('ArgumentHandler.parse_args can only be called once')

		if argv is None:
			argv = sys.argv

		# collect subcommands into _subcommand_lookup
		for cn,cf in registered_subcommands.items():
			self._subcommand_lookup[cn] = cf

		if len(self._subcommand_lookup) == 0:
			self._use_subcommands = False

		# add in subcommands if appropriate
		if not self._use_subcommands:
			if len(self._subcommand_lookup) > 0:
				print('warning: subcommands are not going to be used')
		else:
			self.add_argument('cmd',choices=self._subcommand_lookup.keys())
			self.add_argument('cargs',nargs=argparse.REMAINDER,
								help='arguments for the subcommand')

		# parse arguments
		args = argparse.ArgumentParser.parse_args(self,argv)
		self._has_parse = True
		return args

	def run(self,argv=None,context_fxn=None):
		
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
			# handle the subcommands
			self._subcommand_lookup[args.cmd](context,args.cargs)	

		return
