# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

#!/usr/bin/python

import gzip
import os, inspect
import shutil
from ubiquity import plugin

# Plugin settings
NAME='LICENSE'
AFTER = None
WEIGHT=30
HIDDEN = 'tasks'

class PageGtk(plugin.PluginUI):
    accepted = False

    def __init__(self, controller, *args, **kwargs):
        from gi.repository import Gtk
        label = Gtk.Label("Please review and accept the following licenses")
        label.show_all()
        container = Gtk.VBox()
        container.pack_start(label, True, True, 20)
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        nv_doc_dir = "/usr/share/doc/nvidia-tegra"
        printed_file_list = []
        for myfile in os.listdir(nv_doc_dir):
            myfile = os.path.join(nv_doc_dir, myfile)
            if myfile.endswith(".txt"):
                # copy to /tmp
                tmpfile = os.path.join("/tmp", os.path.basename(myfile))
                shutil.copy(myfile, tmpfile)
            elif myfile.endswith(".txt.gz"):
                # copy to /tmp and decompress
                tmpfile = os.path.join("/tmp", os.path.basename(myfile))
                shutil.copy(myfile, tmpfile)
                newfile = os.path.abspath(tmpfile).rsplit('.gz',1)[0]
                try:
                    with gzip.open(tmpfile, "rt") as gzfile, \
                        open(newfile, "wt") as txtfile:
                        txtfile.write(gzfile.read())
                    tmpfile = newfile
                except:
                    continue
            else:
                continue

            if os.path.basename(tmpfile) in printed_file_list:
                continue
            printed_file_list.append(os.path.basename(tmpfile))
            current_file_basename=os.path.basename(tmpfile).rsplit('.txt',1)[0]
            button = Gtk.Button(current_file_basename)
            button.connect("clicked", self.on_button_clicked, tmpfile)
            container.pack_start(button, True, True, 2)
            button.show()

        checkbox = Gtk.CheckButton('I accept the terms of these licenses')
        checkbox.connect("toggled", self.accept, controller)
        checkbox.show_all()
        container.pack_end(checkbox , False, False, 20)
        self.page = container
        self.controller = controller
        self.plugin_widgets = self.page

    def on_button_clicked(self, widget, lisense_file_path):
        from gi.repository import Gtk
        title = os.path.basename(lisense_file_path).rsplit('.txt',1)[0]
        dialog = Gtk.Dialog(title, widget.get_toplevel(), Gtk.DialogFlags.MODAL)
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CANCEL)
        dialog.set_size_request(500 , 500)
        license_file = open(lisense_file_path , 'r')
        license_file_text = license_file.read()
        license_file.close()
        text = Gtk.TextBuffer();
        text.insert(text.get_iter_at_offset(0), license_file_text, -1)
        license = Gtk.TextView(buffer=text)
        license.set_editable(False)
        scroll = Gtk.ScrolledWindow()
        scroll.set_border_width(10)
        scroll.add(license)
        dialog.vbox.pack_start(scroll, True, True, 0)
        scroll.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            return(True)

    def accept(self, box, controller):
        self.accepted = box.get_active()
        controller.allow_go_forward(self.accepted)

class PageDebconf(plugin.PluginUI):
    plugin_title = 'ubiquity/text/nvlicense_heading_label'

    def __init__(self, controller, *args, **kwargs):
        self.controller = controller

class Page(plugin.Plugin):
    def prepare(self, unfiltered=False):
        if os.environ.get('UBIQUITY_FRONTEND', None) == 'debconf_ui':
            nv_license_script = '/usr/lib/nvidia/license/nvlicense'
            return [nv_license_script]

        # Disable the continue button until the checkbox is toggled
        self.ui.controller.allow_go_forward(self.ui.accepted)
        return plugin.Plugin.prepare(self, unfiltered=unfiltered)
