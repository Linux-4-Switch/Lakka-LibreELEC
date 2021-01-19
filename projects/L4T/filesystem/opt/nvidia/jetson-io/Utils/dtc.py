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

from Utils import syscall
import glob
import os


def __files_exist(*files):
    for f in files:
        if os.path.exists(f) is False:
            raise RuntimeError("File %s not found!" % f)


def __prop_exists(dtb, node, prop):
    return syscall.call('fdtget "%s" "%s" "%s"' % (dtb, node, prop))


def extract(dtb, dts):
    __files_exist(dtb)
    if syscall.call('dtc -I dtb -O dts "%s" -o "%s"' % (dtb, dts)):
        raise RuntimeError("Failed to extract %s to %s!" % (dtb, dts))


def compile(dts, dtb):
    __files_exist(dts)
    if syscall.call('dtc -I dts -O dtb "%s" -o "%s"' % (dts, dtb)):
        raise RuntimeError("Failed to compile %s to %s!" % (dts, dtb))


def overlay(dtb, out, *overlays):
    for overlay in overlays:
        __files_exist(dtb, overlay)
    files = ' '.join(overlays)
    if syscall.call('fdtoverlay -i "%s" -o "%s" "%s"' % (dtb, out, files)):
        raise RuntimeError("Failed to overlay %s with %s!" % (dtb, files))


def get_child_nodes(dtb, node):
    __files_exist(dtb)
    return syscall.call_out('fdtget -l "%s" "%s"' % (dtb, node))


def get_child_props(dtb, node):
    __files_exist(dtb)
    return syscall.call_out('fdtget -p "%s" "%s"' % (dtb, node))


def get_compatible(dtb):
    return get_prop_value(dtb, '/', 'compatible', 0)


def get_model(dtb):
    return get_prop_value(dtb, '/', 'model', 0)


def get_prop_value(dtb, node, prop, index):
    __files_exist(dtb)
    if __prop_exists(dtb, node, prop):
        return None
    values = syscall.call_out('fdtget "%s" "%s" "%s"' % (dtb, node, prop))
    if index >= len(values):
        return None
    return values[index]


def set_prop_value(dtb, node, dtype, prop, value):
    __files_exist(dtb)
    if syscall.call('fdtput -t "%s" "%s" "%s" "%s" "%s"' %
                    (dtype, dtb, node, prop, value)):
        raise RuntimeError("Failed to get property value for %s%s!" %
                           (node, prop))


def find_nodes_with_prop(dtb, node, prop):
    match = []
    cnodes = get_child_nodes(dtb, node)
    for cnode in cnodes:
        cpath = "%s%s/" % (node, cnode)
        match.extend(find_nodes_with_prop(dtb, cpath, prop))
        props = get_child_props(dtb, cpath)
        if prop in props:
            match.append(cpath)
    return match


def find_compatible_dtb_files(compat, model, path):
    dtbs = []
    for dtb in glob.glob(os.path.join(path, '*.dtb')):
        if compat != get_compatible(dtb):
            continue
        if model != get_model(dtb):
            continue
        dtbs.append(dtb)
    if not dtbs:
        return None
    return dtbs


def find_compatible_dtbo_files(compat, path):
    dtbos = []
    for dtbo in glob.glob(os.path.join(path, '*.dtbo')):
        c = get_compatible(dtbo)
        if c is None:
            continue
        if compat in c:
            dtbos.append(dtbo)
    if not dtbos:
        return None
    return dtbos


def remove_node(dtb, node):
    __files_exist(dtb)
    return syscall.call('fdtput -r "%s" "%s"' % (dtb, node))


if syscall.call('which dtc') or syscall.call('which fdtoverlay') or \
   syscall.call('which fdtget') or syscall.call('which fdtput'):
    raise RuntimeError("Device-tree compiler not found!")
