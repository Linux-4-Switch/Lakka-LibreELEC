#!/usr/bin/env python3

# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import argparse
from Jetson import board
import sys


def show_functions(functions):
    for index, function in enumerate(functions):
        print("%2d. %s" % (index + 1, function))


def show_functions_all(functions):
    print("The following functions are supported by the 40-pin header:")
    show_functions(functions)


def show_functions_enabled(jetson, functions):
    enabled = []
    for function in functions:
        if jetson.header.pingroup_is_enabled(function):
            enabled.append(function)

    if not enabled:
        print("No functions are enabled on the 40-pin header.")
    else:
        print("The following functions are enabled on the 40-pin header:")
        show_functions(enabled)


def configure_jetson(jetson, out, functions, available):
    for function in functions:
        if function not in available:
            raise NameError("Function %s is not supported!" % function)

        jetson.header.pingroup_enable(function)

    if out == 'dtb':
        fn = jetson.create_dtb_for_header()
    else:
        fn = jetson.create_dtbo_for_header()
    print("Configuration saved to %s." % fn)


def main():
    parser = argparse.ArgumentParser(
        "Configure Jetson 40-pin expansion header")
    main = parser.add_mutually_exclusive_group(required=True)
    main.add_argument("-l", "--list", choices=['all', 'enabled'],
                      help="List supported functions")
    main.add_argument("-o", "--out", choices=['dtb', 'dtbo'],
                      help="Output DTB or DTBO file")
    parser.add_argument('functions', nargs='*')

    args = parser.parse_args()
    jetson = board.Board()
    available = jetson.header.pingroups_available()

    if len(available) == 0:
        print("No functions supported!")
        sys.exit(0)

    if args.list == 'all':
        show_functions_all(available)
    elif args.list == 'enabled':
        show_functions_enabled(jetson, available)
    else:
        configure_jetson(jetson, args.out, args.functions, available)


if __name__ == '__main__':
    main()
