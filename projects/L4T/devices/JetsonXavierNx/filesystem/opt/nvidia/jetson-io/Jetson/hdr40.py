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

import os
import re
from Jetson import io
from Jetson import pmx
from RPi import hdr40 as rpi
from Utils import dtc


def _header_get_pinmap(dtbo):
    nodes = dtc.find_nodes_with_prop(dtbo, '/', 'nvidia,pins')
    pinmap = []

    for node in nodes:
        res = re.match(r'.*/pin([0-9]*)/', node)
        if res is None:
            continue

        name = dtc.get_prop_value(dtbo, node, 'nvidia,pins', 0)
        pinmap.append(_PinMap(int(res.groups()[0]) - 1, name, node))
    return pinmap


def _header_add_pins(pinmap, names):
    pinmux = pmx.PinMux()
    pins = _HeaderPins(names)
    for pin in pinmap:
        pins.add(pinmux, pin.name, pin.index, pin.node)
    return pins


def _header_add_pingroups(pinmap, pins, d):
    pingroups = io.PinGroups()
    for pin in pinmap:
        for group in d.pingroups.keys():
            for function in pins.get_functions(pin.name):
                if function != d.pingroups[group]:
                    continue

                if group not in d.pingroup_pins.keys():
                    pingroups.add(group, function, pin.name)
                else:
                    for name in d.pingroup_pins[group]:
                        if name == pin.name:
                            pingroups.add(group, function, pin.name)
    return pingroups


class _PinMap(object):
    def __init__(self, index, name, node):
        self.index = index
        self.name = name
        self.node = node


class _HeaderData(object):
    def __init__(self, bdata):
        self.pingroup_pins = bdata['hdr40_pingroup_pins']
        self.pingroups = bdata['hdr40_pingroup_function']
        self.names = bdata['hdr40_pin_names']


class _HeaderPins(object):
    def __init__(self, names):
        r = rpi.Header()
        self.count = r.get_pin_count()
        self.names = [None] * self.count
        self.nodes = {}
        self.pins = {}

        for index in range(self.count):
            if r.pin_is_supply(index):
                name = r.get_pin_name(index)
            elif names is not None and index + 1 in names.keys():
                name = names[index + 1]
            else:
                name = 'unused'
            self.names[index] = name

    def add(self, pinmux, name, index, node):
        if index >= self.count:
            raise IndexError("Invalid pin index %d!" % index)
        if self.names[index] is not 'unused':
            raise IndexError("Duplicate definitions for pin %d!" % index)
        functions = pinmux.pin_get_all_functions(name)
        function = pinmux.pin_get_function(name)
        enabled = pinmux.pin_is_enabled(name)
        self.pins[name] = io.Pin(name, enabled, function, functions)
        self.nodes[name] = node
        self.names[index] = name

    def disable(self, name):
        if name not in self.pins.keys():
            raise NameError("Unknown pin %s!" % name)
        if not self.is_always_enabled(name):
            self.pins[name].disable()

    def disable_all(self):
        for name in self.pins.keys():
            if not self.is_always_enabled(name):
                self.disable(name)

    def get_count(self):
        return self.count

    def get_function(self, name):
        if name not in self.pins.keys():
            raise NameError("Unknown pin %s!" % name)
        return self.pins[name].get_function()

    def get_functions(self, name):
        if name not in self.pins.keys():
            raise NameError("Unknown pin %s!" % name)
        return self.pins[name].get_functions()

    def get_pin_num(self, name):
        return self.names.index(name) + 1

    def get_name(self, index):
        if index >= self.count:
            raise IndexError("Invalid pin index %d!" % index)
        return self.names[index]

    def get_node(self, name):
        if name not in self.nodes.keys():
            raise NameError("Unknown pin %s!" % name)
        if self.nodes[name] is None:
            raise NameError("No node specified for pin %s!" % name)
        return self.nodes[name]

    def is_always_enabled(self, name):
        pin = self.get_pin_num(name)

        # I2C and UART RX/TX pins are
        # always enabled on Jetson platforms.
        if pin in [3, 5, 8, 10, 27, 28]:
            return True
        return False

    def is_configurable(self, name):
        return name in self.pins.keys()

    def is_default(self, name):
        if name not in self.pins.keys():
            raise NameError("Unknown pin %s!" % name)
        return self.pins[name].is_default()

    def is_enabled(self, name):
        if name not in self.pins.keys():
            raise NameError("Unknown pin %s!" % name)
        return self.pins[name].is_enabled()

    def are_default(self):
        for name in self.pins.keys():
            if not self.is_default(name):
                return False
        return True

    def set_default_all(self):
        for name in self.pins.keys():
            self.pins[name].set_default()

    def set_function(self, name, function):
        if name not in self.pins.keys():
            raise NameError("Unknown pin %s!" % name)
        return self.pins[name].set_function(function)


class Header(object):
    def __init__(self, dtbo, d):
        pinmap = _header_get_pinmap(dtbo)
        self.data = _HeaderData(d)
        self.pins = _header_add_pins(pinmap, self.data.names)
        self.pingroups = _header_add_pingroups(pinmap, self.pins, self.data)

    def pin_count(self):
        return self.pins.get_count()

    def pin_get_function(self, name):
        return self.pins.get_function(name)

    def pin_set_function(self, pin, function):
        name = self.pins.get_name(pin - 1)
        return self.pins.set_function(name, function)

    def pin_get_node(self, name):
        return self.pins.get_node(name)

    def pin_get_label(self, pin):
        name = self.pins.get_name(pin - 1)
        if not self.pins.is_configurable(name):
            return name
        if self.pins.is_enabled(name):
            function = self.pins.get_function(name)
            if self.pingroups.pin_is_group(name, function):
                return self.pingroups.get_group(name, function)
            return function
        return 'unused'

    def pin_is_default(self, name):
        return self.pins.is_default(name)

    def pin_is_enabled(self, name):
        return self.pins.is_enabled(name)

    def pins_are_default(self):
        return self.pins.are_default()

    def pins_set_default(self):
        self.pins.set_default_all()

    def pins_reset(self):
        self.pins.disable_all()

    def pingroups_available(self):
        return sorted(self.pingroups.get_available())

    def pingroup_enable(self, group):
        pins = self.pingroups.get_pins(group)
        function = self.pingroups.get_function(group)
        for pin in pins:
            current = self.pins.get_function(pin)
            if current == function:
                continue
            if self.pins.is_enabled(pin):
                self.pingroup_disable(current)
        for pin in pins:
            self.pins.set_function(pin, function)

    def pingroup_disable(self, group):
        pins = self.pingroups.get_pins(group)
        for pin in pins:
            self.pins.disable(pin)

    def pingroup_is_enabled(self, group):
        pins = self.pingroups.get_pins(group)
        function = self.pingroups.get_function(group)
        for pin in pins:
            if self.pins.get_function(pin) != function:
                return False
        return True

    def pingroup_get_pins(self, group):
        indices = []
        pins = self.pingroups.get_pins(group)
        for pin in pins:
            indices.append(self.pins.get_pin_num(pin))
        return ','.join(map(str, sorted(indices)))
