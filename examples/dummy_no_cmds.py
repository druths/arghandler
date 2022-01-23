#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK

from arghandler import ArgumentHandler, subcmd

if __name__ == '__main__':
    handler = ArgumentHandler(enable_autocompletion=True)

    args = handler.parse_args()

    print('done')
