#!/usr/bin/env python

# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
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

import os
import subprocess
from ubiquity import plugin

# Plugin settings
NAME = 'nv-swap'
AFTER = 'nv-resizefs'
WEIGHT = 30

class PageGtk(plugin.PluginUI):
    plugin_title = 'ubiquity/text/nv_swap_label'

    def __init__(self, controller, *args, **kwargs):
        super(PageGtk, self).__init__(self, *args, **kwargs)
        self.script = '/usr/lib/nvidia/swap/nvswap.sh'

        if not self.check_pre_req():
            return

        from gi.repository import Gtk

        container = Gtk.VBox(spacing=20)
        container.set_border_width(20)
        container.set_homogeneous(False)

        label_description = Gtk.Label(
                'It is recommended to create a 4GB disk SWAP file if you intent to use the device for AI and Deep Learning.\n' +
                'For example, training under PyTorch using the GPU.')
        label_description.set_justify(Gtk.Justification.LEFT)
        label_description.show()
        container.pack_start(label_description, False, False, 0)


        self.button1 = Gtk.RadioButton(label="Create SWAP File (Recommended)")
        #button1.connect("toggled", self.toggled_cb)
        self.button1.show()
        container.pack_start(self.button1, False, False, 0)

        self.button2 = Gtk.RadioButton.new_from_widget(self.button1)
        self.button2.set_label("Do not create SWAP File")
        #button2.connect("toggled", self.toggled_cb)
        self.button2.set_active(False)
        self.button2.show()
        container.pack_start(self.button2, False, False, 0)

        label2 = Gtk.Label(
                'Please note that having a SWAP file may shorten life of SDCARD due to increased writes to the medium.\n' +
                'You can manually enable SWAP at a later time by following "Enable Disk SWAP" section in L4T Developer Guide.')
        label2.set_justify(Gtk.Justification.LEFT)
        label2.show()
        container.pack_start(label2, False, False, 0)


        self.page = container
        self.controller = controller
        self.plugin_widgets = self.page

    def plugin_on_next_clicked(self):
        if self.button1.get_active():
            subprocess.check_output([self.script, '-s'], universal_newlines=True).strip()

    def check_pre_req(self):
        if not os.path.exists(self.script):
            return False

        # Query whether current platform is supported to resize fs
        support_swap = subprocess.check_output(
                [self.script, '-c'], universal_newlines=True).strip()
        if support_swap == 'false':
            return False

        return True

class PageDebconf(plugin.Plugin):
    plugin_title = 'ubiquity/text/nv_swap_label'

    def __init__(self, controller, *args, **kwargs):
        super(PageDebconf, self).__init__(self, *args, **kwargs)
        self.controller = controller

class Page(plugin.Plugin):
    def prepare(self, unfiltered=False):
        if os.environ.get('UBIQUITY_FRONTEND', None) == 'debconf_ui':
            nv_swap_script = '/usr/lib/nvidia/swap/nvswap-query'
            return [nv_swap_script]
        return
