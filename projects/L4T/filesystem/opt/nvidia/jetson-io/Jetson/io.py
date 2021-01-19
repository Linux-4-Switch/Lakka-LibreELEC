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


class PinGroup(object):
    def __init__(self, function):
        self.pins = set()
        self.function = function

    def add_pin(self, pin):
        self.pins.add(pin)


class PinGroups(object):
    def __init__(self):
        self.groups = {}
        self.available = set()

    def add(self, group, function, pin):
        if group not in self.available:
            self.groups[group] = PinGroup(function)
        else:
            if function != self.groups[group].function:
                raise RuntimeError("Function mismatch for group %s!" % group)
        self.available.add(group)
        self.groups[group].add_pin(pin)

    def get_available(self):
        return self.available

    def get_function(self, group):
        if group not in self.available:
            raise NameError("Pin group %s is not supported!" % group)
        return self.groups[group].function

    def get_group(self, pin, function):
        for group in self.available:
            if function == self.groups[group].function:
                if pin in self.groups[group].pins:
                    return group
        return None

    def get_pins(self, group):
        if group not in self.available:
            raise NameError("Pin group %s is not supported!" % group)
        return self.groups[group].pins

    def pin_is_group(self, pin, function):
        group = self.get_group(pin, function)
        if group and len(self.groups[group].pins) == 1:
            return True
        return False


class PinState(object):
    def __init__(self, enabled):
        self.current = enabled
        self.default = enabled

    def enable(self):
        self.current = True

    def disable(self):
        self.current = False

    def is_default(self):
        return self.current == self.default

    def is_enabled(self):
        return self.current is True

    def set_default(self):
        self.current = self.default


class PinFunction(object):
    def __init__(self, current, available):
        self.current = current
        self.default = current
        self.reserved = None
        self.available = available

        if 'rsvd' in current:
            self.reserved = current
        else:
            for function in available:
                if 'rsvd' in function:
                    self.reserved = function

    def get_available(self):
        return self.available

    def set_reserved(self):
        if self.reserved is not None:
            self.current = self.reserved

    def is_reserved(self):
        if self.reserved is not None:
            return self.current == self.reserved
        return False

    def is_default(self):
        return self.current == self.default

    def set_default(self):
        self.current = self.default

    def get(self):
        return self.current

    def set(self, function):
        if function not in self.available:
            raise RuntimeError("Invalid function %s!" % function)
        self.current = function


class Pin(object):
    def __init__(self, name, enabled, function, functions):
        if function not in functions:
            raise RuntimeError("Invalid function %s for pin %s!" %
                               (function, name))

        self.function = PinFunction(function, functions)
        self.state = PinState(enabled)
        self.name = name

    def disable(self):
        self.function.set_reserved()
        self.state.disable()

    def is_default(self):
        if not self.function.is_default():
            return False
        if not self.state.is_default():
            return False
        return True

    def is_enabled(self):
        if self.function.is_reserved():
            return False
        return self.state.is_enabled()

    def set_default(self):
        self.function.set_default()
        self.state.set_default()

    def get_function(self):
        return self.function.get()

    def get_functions(self):
        return self.function.get_available()

    def set_function(self, function):
        self.function.set(function)
        if self.function.is_reserved():
            self.state.disable()
        else:
            self.state.enable()
