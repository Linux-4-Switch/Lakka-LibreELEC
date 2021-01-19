# Copyright (c) 2019-2020, NVIDIA CORPORATION. All rights reserved.
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
from Linux import extlinux
from Jetson import hdr40
from Utils import dtc
from Utils import fio
from Utils import syscall
import datetime
import glob
import os
import re
import shutil


def _board_find_hw_addon_overlays(dtbos):
    hw_addons = {}

    for dtbo in dtbos:
        name = dtc.get_prop_value(dtbo, '/', 'overlay-name', 0)
        if name is None:
            continue

        if name == 'Jetson 40pin Header':
            continue

        if name in hw_addons.keys():
            error = "Multiple DT overlays for '%s' found!\n" % name
            error = error + "Please remove duplicate(s)"
            error = error + "\n%s\n%s" % (dtbo, hw_addons[name])
            raise RuntimeError(error)
        hw_addons[name] = dtbo
    return hw_addons


def _board_find_header_overlay(dtbos):
    header = None

    for dtbo in dtbos:
        name = dtc.get_prop_value(dtbo, '/', 'overlay-name', 0)
        if name is None:
            continue

        if name == 'Jetson 40pin Header':
            if header:
                error = "Multiple DT overlays for '%s' found!\n" % name
                error = error + "Please remove duplicate(s)"
                error = error + "\n%s\n%s" % (dtbo, header)
                raise RuntimeError(error)
            header = dtbo

    if header is None:
        raise RuntimeError("DT Overlay for 40pin Header not found!")
    return header


def _board_get(compat):
    dn = os.path.dirname(os.path.abspath(__file__))
    for fn in glob.glob(os.path.join(dn, 'boards/*.board')):
        board = os.path.splitext(os.path.basename(fn))[0]
        if board in compat:
            return board
    raise RuntimeError("No board data found!")


def _board_get_dtb(compat, model, path):
    dtbs = dtc.find_compatible_dtb_files(compat, model, path)

    if dtbs is None:
        raise RuntimeError("No DTB found for %s!" % model)
    if len(dtbs) > 1:
        raise RuntimeError("Multiple DTBs found for %s!" % model)
    return dtbs[0]


def _board_load_data(board):
    dn = os.path.dirname(os.path.abspath(__file__))
    fn = os.path.join(dn, "boards/%s.board" % board)
    if os.path.exists(fn) is False:
        raise RuntimeError("Board %s not supported!" % board)
    data = {}
    with open(fn) as f:
        code = compile(f.read(), fn, 'exec')
        exec(code, globals(), data)
    return data


def _board_partition_is_mounted(partlabel):
    if not syscall.call_out('findfs PARTLABEL="%s"' % partlabel):
        raise RuntimeError("No %s partition found!" % partlabel)
    return syscall.call('findmnt -n -S PARTLABEL="%s"' % partlabel) == 0


def _board_partition_mount(partlabel):
    path = os.path.join('/mnt', partlabel)
    if os.path.exists(path):
        raise RuntimeError("Mountpoint %s already exists!" % path)
    os.makedirs(path)
    syscall.call('mount PARTLABEL="%s" "%s"' % (partlabel, path))
    return path


def _board_partition_umount(mountpoint):
    if syscall.call('umount "%s"' % mountpoint):
        raise RuntimeError("Failed to umount %s!" % mountpoint)
    os.rmdir(mountpoint)


class Board(object):
    def __init__(self):
        self.appdir = None
        self.bootdir = '/boot'
        self.extlinux = '/boot/extlinux/extlinux.conf'
        dtbdir = os.path.join(self.bootdir, 'dtb')
        fio.is_rw(self.bootdir)

        # When mounting the rootfs via NFS, the APP partition is not
        # mounted, but this is the partition that the bootloader reads to
        # parse the extlinux.conf and loads the kernel DTB. Therefore, if
        # the rootfs is mounted using NFS, it is necessary to mount this
        # partition and copy the generated files back to this partition.
        if not _board_partition_is_mounted('APP'):
            self.appdir = _board_partition_mount('APP')
            dtbdir = os.path.join(self.appdir, 'boot/dtb')
            fio.is_rw(self.appdir)

        self.compat = dt.read_prop('compatible')
        self.model = dt.read_prop('model')
        self.name = _board_get(self.compat)
        self.data = _board_load_data(self.name)
        self.dtb = _board_get_dtb(self.compat, self.model, dtbdir)
        dtbos = dtc.find_compatible_dtbo_files(self.name, self.bootdir)
        self.hdtbo = _board_find_header_overlay(dtbos)
        self.hw_addons = _board_find_hw_addon_overlays(dtbos)
        self.header = hdr40.Header(self.hdtbo, self.data)

    def __del__(self):
        if self.appdir:
            _board_partition_umount(self.appdir)

    def get_dtb_basename(self):
        return os.path.splitext(os.path.basename(self.dtb))[0]

    def gen_dtb_filename(self, suffix, path):
        basename = self.get_dtb_basename()
        name = "%s-%s.dtb" % (basename, suffix)
        return os.path.join(path, name)

    def hw_addon_get(self):
        return sorted(self.hw_addons.keys())

    def hw_addon_load(self, name):
        if name not in self.hw_addons.keys():
            raise RuntimeError("No overlay found for %s!" % name)

        overlay = self.hw_addons[name]
        self.header.pins_reset()

        nodes = dtc.find_nodes_with_prop(overlay, '/', 'nvidia,function')

        for node in nodes:
            res = re.match(r'.*/pin([0-9]*)/', node)
            if res is None:
                raise RuntimeError("Failed to get pin number for node %s!" %
                                   node)

            pin = int(res.groups()[0])
            function = dtc.get_prop_value(overlay, node, 'nvidia,function', 0)
            self.header.pin_set_function(pin, function)

    def _create_header_dtbo(self, name):
        dtbo = os.path.join(self.bootdir, name)
        shutil.copyfile(self.hdtbo, dtbo)

        for pin in self.header.pins.pins.keys():
            function = self.header.pin_get_function(pin)
            node = self.header.pin_get_node(pin)

            if self.header.pin_is_enabled(pin):
                dtc.set_prop_value(dtbo, node, 's', 'nvidia,function',
                                   function)
            else:
                if self.header.pin_is_default(pin):
                    dtc.remove_node(dtbo, node)
                else:
                    if function is not None:
                        dtc.set_prop_value(dtbo, node, 's', 'nvidia,function',
                                           function)

                    dtc.set_prop_value(dtbo, node, 'u', 'nvidia,tristate', '1')
                    dtc.set_prop_value(dtbo, node, 'u', 'nvidia,enable-input',
                                       '0')

        return dtbo

    def create_dtbo_for_header(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        name = "User Custom [%s]" % date
        fn = "%s-user-custom.dtbo" % self.get_dtb_basename()
        dtbo = self._create_header_dtbo(fn)
        dtc.set_prop_value(dtbo, '/', 's', 'overlay-name', "%s" % name)
        return dtbo

    def create_dtb_for_hw_addon(self, name):
        if name not in self.hw_addons.keys():
            raise RuntimeError("Unknown hardware addon %s!" % name)
        dtbo = self.hw_addons[name]
        suffix = name.replace(' ', '-').lower()
        dtb = self.gen_dtb_filename(suffix, self.bootdir)
        dtc.overlay(self.dtb, dtb, dtbo)
        if self.appdir:
            appextlinux = os.path.join(self.appdir, self.extlinux[1:])
            extlinux.add_entry(appextlinux, name, name, dtb, True)
            shutil.copyfile(dtb, os.path.join(self.appdir, dtb[1:]))
            shutil.copyfile(appextlinux, self.extlinux)
        else:
            extlinux.add_entry(self.extlinux, name, name, dtb, True)
        return dtb

    def create_dtb_for_header(self):
        dtb = self.gen_dtb_filename("user-custom", self.bootdir)
        try:
            dtbo = self._create_header_dtbo('jetson-user-custom.dtbo')
            dtc.overlay(self.dtb, dtb, dtbo)
        except Exception:
            raise
        finally:
            if os.path.exists(dtbo):
                os.remove(dtbo)

        name = "Custom 40-pin Header Config"
        if self.appdir:
            appextlinux = os.path.join(self.appdir, self.extlinux[1:])
            extlinux.add_entry(appextlinux, 'JetsonIO', name, dtb, True)
            shutil.copyfile(dtb, os.path.join(self.appdir, dtb[1:]))
            shutil.copyfile(appextlinux, self.extlinux)
        else:
            extlinux.add_entry(self.extlinux, 'JetsonIO', name, dtb, True)
        return dtb
