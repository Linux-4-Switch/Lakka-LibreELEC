#!/usr/bin/env python

# Copyright (c) 2019-2020, NVIDIA CORPORATION.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os, inspect
import shutil
import subprocess
from ubiquity import plugin

# Plugin settings
NAME = 'nv-resizefs'
AFTER = 'usersetup'
WEIGHT = 30

class PageGtk(plugin.PluginUI):
    plugin_title = 'ubiquity/text/nv_resizefs_label'

    def __init__(self, controller, *args, **kwargs):
        super(PageGtk, self).__init__(self, *args, **kwargs)
        self.script = '/usr/lib/nvidia/resizefs/nvresizefs.sh'

        if not self.check_pre_req():
            return None

        self.max_size = self.get_max_size()
        self.current_size = self.get_current_size()
        self.desired_size = self.max_size

        from gi.repository import Gtk

        container = Gtk.VBox(spacing=20)
        container.set_border_width(20)
        container.set_homogeneous(False)

        label_description = Gtk.Label(
                'Please enter desired size of APP partition in Megabytes (MB).\n' +
                'Default value in input field is the maximum size that can be accepted.\n' +
                'Enter 0 or leave blank to use the maximum size value.')
        label_description.set_justify(Gtk.Justification.CENTER)
        label_description.show()
        container.pack_start(label_description, False, False, 0)

        self.label_size = Gtk.Label()
        self.update_label_size()
        self.label_size.show()
        container.pack_start(self.label_size, False, False, 0)

        self.entry_size = Gtk.Entry()
        self.entry_size.set_text(str(self.desired_size))
        self.entry_size.connect('insert-text', self.on_insert_text_size)
        self.entry_size.connect('changed', self.on_changed_text_size)
        self.entry_size.show()
        container.pack_start(self.entry_size, False, False, 0)

        self.page = container
        self.controller = controller
        self.plugin_widgets = self.page

    def on_insert_text_size(self, entry, text, length, position):
        if text.isdigit():
            return position
        entry.stop_emission('insert-text')

    def on_changed_text_size(self, entry):
        text = entry.get_text()
        try:
            input_size = int(text)
        except:
            input_size = 0

        if (input_size == 0 or
            (input_size >= self.current_size and input_size <= self.max_size)):
            self.desired_size = input_size
            self.controller.allow_go_forward(True)
        else:
            self.controller.allow_go_forward(False)

    def update_label_size(self):
        self.label_size.set_text(
                'Current size: %d MB, Maximum accepted size: %d MB'
                % (self.current_size, self.max_size))

    def plugin_on_next_clicked(self):
        self.set_partition_size(self.desired_size)
        if self.desired_size == 0:
            self.desired_size = self.max_size
        self.current_size = self.desired_size

    def check_pre_req(self):
        if not os.path.exists(self.script):
            return False

        # Query whether current platform is supported to resize fs
        support_resizefs = subprocess.check_output(
                [self.script, '-c'], universal_newlines=True).strip()
        if support_resizefs == 'false':
            return False

        return True

    def get_max_size(self):
        return int(subprocess.check_output(
                [self.script, '-m'], universal_newlines=True).strip())

    def get_current_size(self):
        return int(subprocess.check_output(
                [self.script, '-g'], universal_newlines=True).strip())

    def set_partition_size(self, size):
        result = ""
        if size != 0:
            result = subprocess.check_output(
                    [self.script, '-s', str(size)], universal_newlines=True).strip()
        else:
            result = subprocess.check_output(
                    [self.script], universal_newlines=True).strip()

        if result:
            print(result)

class PageDebconf(plugin.Plugin):
    plugin_title = 'ubiquity/text/nv_resizefs_label'

    def __init__(self, controller, *args, **kwargs):
        super(PageDebconf, self).__init__(self, *args, **kwargs)
        self.controller = controller

class Page(plugin.Plugin):
    def prepare(self, unfiltered=False):
        if os.environ.get('UBIQUITY_FRONTEND', None) == 'debconf_ui':
            nv_resizefs_script = '/usr/lib/nvidia/resizefs/nvresizefs-query'
            return [nv_resizefs_script]
