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

from Linux import dt
from Linux import pinctrl
import os
import re


class _PinConfig(object):
    def __init__(self, function, tristate, input_en):
        self.function = function
        self.tristate = tristate
        self.input_en = input_en


def _get_pinconfig(dev):
    pinconfs = pinctrl.get_pinconf_groups(dev)

    conf = {}
    index = 0
    name = None
    function = None
    tristate = None
    input_en = None

    for pinconf in pinconfs:
        res = re.match(r'%d \(([0-z_]*)\):' % index, pinconf)
        if res:
            name = res.groups()[0]
            function = None
            tristate = None
            input_en = None
            index = index + 1
            continue

        if name is None:
            continue

        res = re.match(r'\ttristate=([0-1]*)', pinconf)
        if res:
            tristate = res.groups()[0]

        res = re.match(r'\tenable-input=([0-1]*)', pinconf)
        if res:
            input_en = res.groups()[0]

        res = re.match(r'\tfunc=([0-z]*)', pinconf)
        if res:
            function = res.groups()[0]

        if function and tristate and input_en:
            conf[name] = _PinConfig(function, tristate, input_en)
            name = None

    return conf


class PinMux(object):
    def __init__(self):
        dev = dt.read_prop('__symbols__/pinmux').split('pinmux@')[1]
        self.pinconfig = _get_pinconfig(dev)
        self.functions = pinctrl.get_pinmux_functions(dev)

    def pin_get_function(self, pin):
        if pin not in self.pinconfig.keys():
            raise RuntimeError("Function for pin %s not found!" % pin)

        return self.pinconfig[pin].function

    def pin_get_all_functions(self, pin):
        functions = []

        for line in self.functions:
            if pin not in line:
                continue

            res = re.match(r'function: ([0-z]*), .*', line)
            if res is None:
                raise RuntimeError("Function for pin %s not found!" % pin)

            functions.append(res.groups()[0])

        return sorted(functions)

    def pin_is_enabled(self, pin):
        if pin not in self.pinconfig.keys():
            raise RuntimeError("Function for pin %s not found!" % pin)

        if self.pinconfig[pin].tristate == '0':
            return True
        return self.pinconfig[pin].input_en == '1'
