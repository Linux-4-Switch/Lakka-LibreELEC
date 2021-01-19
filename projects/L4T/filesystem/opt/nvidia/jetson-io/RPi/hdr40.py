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


class Header(object):
    pins = [
        # label,                type
        {'label': '3.3V',      'type': 'Power'},
        {'label': '5V',        'type': 'Power'},
        {'label': 'BCM 2',     'type': 'IO'},
        {'label': '5V',        'type': 'Power'},
        {'label': 'BCM 3',     'type': 'IO'},
        {'label': 'GND',       'type': 'Ground'},
        {'label': 'BCM 4',     'type': 'IO'},
        {'label': 'BCM 14',    'type': 'IO'},
        {'label': 'GND',       'type': 'Ground'},
        {'label': 'BCM 15',    'type': 'IO'},
        {'label': 'BCM 17',    'type': 'IO'},
        {'label': 'BCM 18',    'type': 'IO'},
        {'label': 'BCM 27',    'type': 'IO'},
        {'label': 'GND',       'type': 'Ground'},
        {'label': 'BCM 22',    'type': 'IO'},
        {'label': 'BCM 23',    'type': 'IO'},
        {'label': '3.3V',      'type': 'Power'},
        {'label': 'BCM 24',    'type': 'IO'},
        {'label': 'BCM 10',    'type': 'IO'},
        {'label': 'GND',       'type': 'Ground'},
        {'label': 'BCM 9',     'type': 'IO'},
        {'label': 'BCM 25',    'type': 'IO'},
        {'label': 'BCM 11',    'type': 'IO'},
        {'label': 'BCM 8',     'type': 'IO'},
        {'label': 'GND',       'type': 'Ground'},
        {'label': 'BCM 7',     'type': 'IO'},
        {'label': 'BCM 0',     'type': 'IO'},
        {'label': 'BCM 1',     'type': 'IO'},
        {'label': 'BCM 5',     'type': 'IO'},
        {'label': 'GND',       'type': 'Ground'},
        {'label': 'BCM 6',     'type': 'IO'},
        {'label': 'BCM 12',    'type': 'IO'},
        {'label': 'BCM 13',    'type': 'IO'},
        {'label': 'GND',       'type': 'Ground'},
        {'label': 'BCM 19',    'type': 'IO'},
        {'label': 'BCM 16',    'type': 'IO'},
        {'label': 'BCM 26',    'type': 'IO'},
        {'label': 'BCM 20',    'type': 'IO'},
        {'label': 'GND',       'type': 'Ground'},
        {'label': 'BCM 21',    'type': 'IO'}]

    def pin_is_supply(self, index):
        if Header.pins[index]['type'] == 'IO':
            return False
        return True

    def get_pin_name(self, index):
        return Header.pins[index]['label']

    def get_pin_count(self):
        return len(Header.pins)
