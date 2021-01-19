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


def show_hardware(hwlist):
    print("Configurations for the following hardware modules are available:")
    for index, hw in enumerate(hwlist):
        print("%d. %s" % (index + 1, hw))


def configure_jetson(jetson, hwlist, hw):
    if hw not in hwlist:
        raise NameError("No configuration found for %s!" % hw)
    jetson.hw_addon_load(hw)
    fn = jetson.create_dtb_for_hw_addon(hw)
    print("Configuration saved to %s." % fn)


def main():
    parser = argparse.ArgumentParser("Configure Jetson for a hardware module")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--name", help="Name of hardware module")
    group.add_argument("-l", "--list", help="List of hardware modules",
                       action='store_true')
    args = parser.parse_args()

    jetson = board.Board()
    hwlist = jetson.hw_addon_get()

    if len(hwlist) == 0:
        print("No hardware configurations found!")
        sys.exit(0)

    if args.list:
        show_hardware(hwlist)
    else:
        configure_jetson(jetson, hwlist, args.name)


if __name__ == '__main__':
    main()
