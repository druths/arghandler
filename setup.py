#!/usr/bin/env python

from distutils.core import setup

setup(	name='arghandler',
		version='1.0.3',
		description='argparse extended with awesome feature enhancements to make life easier',
		author='Derek Ruths',
		author_email='druths@networkdynamics.org',
		url='http://www.github.com/druths/arghandler',
		packages=['arghandler','arghandler.tests'],

		license='Apache',

		classifiers=[
			'Development Status :: 4 - Beta',

			'Intended Audience :: Developers',
			'Topic :: Software Development',

			'License :: OSI Approved :: Apache Software License',

			'Programming Language :: Python :: 2.7',
			'Programming Language :: Python :: 3',
			'Programming Language :: Python :: 3.2',
			'Programming Language :: Python :: 3.3',
			'Programming Language :: Python :: 3.4'
		],
		keywords='argparse command-line parsing'
	)
