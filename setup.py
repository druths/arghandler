#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(  name='arghandler',
        version='1.3.1',
        description='argparse extended with awesome feature enhancements to make life easier',
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Derek Ruths',
        author_email='druths@networkdynamics.org',
        url='http://www.github.com/druths/arghandler',
        packages=['arghandler','arghandler.tests'],

        install_requires=['argcomplete'],

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
