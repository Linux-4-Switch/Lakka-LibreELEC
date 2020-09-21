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

from curses import panel
import curses
from Jetson import board
import os
import shutil
import sys
import textwrap


class Window(object):
    def __init__(self, screen, h, w, y, x):
        self.h = h
        self.w = w
        self.win = curses.newwin(h, w, y, x)
        self.panel = panel.new_panel(self.win)
        self.win.clear()
        self.panel.hide()
        panel.update_panels()

    def clear(self):
        self.win.clear()

    def show(self):
        self.panel.top()
        self.panel.show()
        self.win.refresh()
        panel.update_panels()
        curses.doupdate()

    def hide(self):
        self.panel.bottom()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

    def addstr_centre(self, y, text, mode=curses.A_NORMAL):
        x = int((self.w / 2) - (len(text) / 2))
        if x > 0:
            self.win.addstr(y, x, text, mode)
            return 1
        else:
            for i, t in enumerate(textwrap.wrap(text, self.w)):
                x = int((self.w / 2) - (len(t) / 2))
                self.win.addstr(y + i, x, t, mode)
            return i


class MenuItem(object):
    def __init__(self, name, exit_on_select=False):
        self.name = name
        self.exit_on_select = exit_on_select

    def get_caption(self, maxwidth):
        return self.name

    def is_empty(self):
        return self.name is None


class MenuItemAction(MenuItem):
    def __init__(self, name, exit_on_select, action, *args):
        MenuItem.__init__(self, name, exit_on_select)
        self.action = action
        self.args = args

    def do_action(self):
        if self.args:
            self.action(self.args)
        else:
            self.action()


class MenuItemSelectable(MenuItemAction):
    def __init__(self, name, is_selected, action, *args):
        MenuItemAction.__init__(self, name, False, action, *args)
        self.is_selected = is_selected

    def get_caption(self, maxwidth):
        if self.is_selected(self.args):
            return "[*] %s" % self.name.ljust(maxwidth)
        return "[ ] %s" % self.name.ljust(maxwidth)


class Menu(object):
    def __init__(self, win, title, maxwidth=0):
        self.win = win
        self.win.win.keypad(1)
        self.title = title
        self.maxwidth = maxwidth
        self.index = 0

    def up(self, items):
        while self.index > 0:
            self.index = self.index - 1
            if not items[self.index].is_empty():
                return

    def down(self, items):
        while self.index < len(items) - 1:
            self.index = self.index + 1
            if not items[self.index].is_empty():
                return

    def select(self, items):
        item = items[self.index]

        if hasattr(item, 'do_action'):
            item.do_action()

        if item.exit_on_select:
            self.index = 0

        return item.exit_on_select

    def update(self, items):
        for index, item in enumerate(items):
            if item.is_empty():
                continue

            caption = item.get_caption(self.maxwidth)

            if index == self.index:
                self.win.addstr_centre(4+index, caption, curses.A_REVERSE)
            else:
                self.win.addstr_centre(4+index, caption)

    def show(self, items):
        self.win.show()
        self.win.addstr_centre(2, self.title)

        while True:
            self.update(items)
            key = self.win.win.getch()

            if key in [curses.KEY_ENTER, ord(' '), ord('\n')]:
                if self.select(items):
                    break

            elif key == curses.KEY_UP:
                self.up(items)

            elif key == curses.KEY_DOWN:
                self.down(items)

        self.win.hide()


class Header(object):
    def __init__(self, screen, jetson, w):
        self.rows = int(jetson.header.pin_count() / 2)
        self.win = Window(screen, self.rows + 2, w, 4, 2)
        self.jetson = jetson

    def show(self):
        self.update()
        self.win.show()

    def clear(self):
        self.win.clear()

    def update(self):
        self.clear()

        for row in range(self.rows):
            pin = (row * 2) + 1
            odd = self.jetson.header.pin_get_label(pin)
            even = self.jetson.header.pin_get_label(pin + 1)
            text = "%s (%2d)  (%2d) %s" % (odd, pin, pin + 1, even)
            col = int(self.win.w / 2) - len("%s (%2d) " % (odd, row))
            self.win.win.addstr(row, col, text)


class HardwareAddonsMenu(object):
    def __init__(self, screen, header, jetson, h, w):
        title = "Select one of the following options:"
        self.win = Window(screen, h, w, 2, 2)
        self.header = header
        self.jetson = jetson
        self.addon = None
        self.menuitems = []

        for addon in self.jetson.hw_addon_get():
            item = MenuItemAction(addon, True, self.select, addon)
            self.menuitems.append(item)
        self.menuitems.append(MenuItem(None))
        self.menuitems.append(MenuItem('Back', True))
        self.menu = Menu(self.win, title)

    def deselect(self):
        self.addon = None

    def get(self):
        return self.addon

    def select(self, args):
        self.jetson.hw_addon_load(args[0])
        self.header.update()
        self.addon = args[0]

    def show(self):
        self.addon = None
        self.menu.show(self.menuitems)


class PinGroupMenu(object):
    def __init__(self, screen, header, jetson, h, w):
        title = "Select desired functions (for pins):"
        self.win = Window(screen, h, w, 2, 2)
        self.header = header
        self.jetson = jetson
        self.menuitems = []
        maxwidth = 0

        pingroups = self.jetson.header.pingroups_available()
        maxlen = len(max(pingroups, key=len))

        for pingroup in pingroups:
            pins = self.jetson.header.pingroup_get_pins(pingroup)
            text = "%s (%s)" % (pingroup.ljust(maxlen), pins)
            item = MenuItemSelectable(text, self.is_selected,
                                      self.set_pingroup, pingroup)
            self.menuitems.append(item)
            if maxwidth < len(text):
                maxwidth = len(text)
        self.menuitems.append(MenuItem(None))
        self.menuitems.append(MenuItem('Back', True))
        self.menu = Menu(self.win, title, maxwidth)

    def is_selected(self, args):
        return self.jetson.header.pingroup_is_enabled(args[0])

    def show(self):
        self.menu.show(self.menuitems)

    def set_pingroup(self, args):
        if self.jetson.header.pingroup_is_enabled(args[0]):
            self.jetson.header.pingroup_disable(args[0])
        else:
            self.jetson.header.pingroup_enable(args[0])
        self.header.update()


class MainMenu(object):
    def __init__(self, screen, main, h, w):
        self.jetson = board.Board()
        self.header = Header(screen, self.jetson, w)
        self.pingroup = PinGroupMenu(screen, self.header, self.jetson, h, w)
        self.hw_addons = HardwareAddonsMenu(screen, self.header, self.jetson,
                                            h, w)

        title = "Select one of the following options:"
        self.subwin = Window(screen, 10, w, self.header.win.h + 3, 2)
        self.main = main

        self.menu_default = []
        self.menu_save_hw_addons = []
        self.menu_save_pingroup = []

        caption = 'Configure Jetson for compatible hardware'
        item = MenuItemAction(caption, True, self.hw_addons.show)
        self.menu_default.append(item)
        caption = 'Configure 40-pin expansion header'
        item = MenuItemAction(caption, True, self.pingroup.show)
        self.menu_default.append(item)

        caption = 'Save and reboot to reconfigure pins'
        item = MenuItemAction(caption, False, self.create_dtb_and_reboot)
        self.menu_save_hw_addons.append(item)
        self.menu_save_pingroup.append(item)

        caption = 'Save and exit without rebooting'
        item = MenuItemAction(caption, False, self.create_dtb_and_exit)
        self.menu_save_hw_addons.append(item)
        self.menu_save_pingroup.append(item)

        caption = 'Export as Device-Tree Overlay'
        item = MenuItemAction(caption, False, self.create_dtbo_and_exit)
        self.menu_save_pingroup.append(item)

        item = MenuItemAction('Discard pin changes', True, self.discard)
        self.menu_save_hw_addons.append(item)
        self.menu_save_pingroup.append(item)

        item = MenuItemAction('Exit', False, sys.exit)
        self.menu_default.append(item)
        self.menu_save_hw_addons.append(item)
        self.menu_save_pingroup.append(item)

        self.menu = Menu(self.subwin, title)

    def create_dtb(self):
        name = self.hw_addons.get()
        if name:
            dtb = self.jetson.create_dtb_for_hw_addon(name)
        else:
            dtb = self.jetson.create_dtb_for_header()
        return dtb

    def create_dtb_and_exit(self):
        dtb = self.create_dtb()
        messages = []
        messages.append("Configuration saved to file %s." % dtb)
        messages.append("Reboot system to reconfigure.")
        messages.append("Press any key to exit")
        self.exit(messages, False)

    def create_dtb_and_reboot(self):
        dtb = self.create_dtb()
        messages = []
        messages.append("Configuration saved to file %s." % dtb)
        messages.append("Press any key to reboot the system now"
                        " or Ctrl-C to abort")
        self.exit(messages, True)

    def create_dtbo_and_exit(self):
        dtbo = self.jetson.create_dtbo_for_header()
        messages = []
        messages.append("Configuration saved to file %s." % dtbo)
        messages.append("Press any key to exit")
        self.exit(messages, False)

    def discard(self):
        self.hw_addons.deselect()
        self.jetson.header.pins_set_default()
        self.header.show()

    def exit(self, messages, reboot):
        self.header.clear()
        self.main.print_and_wait(messages)
        if reboot:
            os.system('reboot')
        else:
            sys.exit(0)

    def show(self):
        while True:
            self.subwin.win.clear()
            self.header.show()
            if self.jetson.header.pins_are_default():
                self.menu.show(self.menu_default)
            elif self.hw_addons.get() is not None:
                self.menu.show(self.menu_save_hw_addons)
            else:
                self.menu.show(self.menu_save_pingroup)


class MainWindow(object):
    def __init__(self, screen, h, w):
        title = " Jetson Expansion Header Tool "
        self.main = Window(screen, h, w, 1, 1)
        self.main.win.border('|', '|', '=', '=', ' ', ' ', ' ', ' ')
        self.main.addstr_centre(0, title)
        self.main.show()

        y, x = screen.getmaxyx()
        if h > y or w > x:
            messages = []
            messages.append("Failed to resize terminal!")
            messages.append("Please try executing 'resize' and try again.")
            messages.append("Press any key to exit")
            self.print_and_wait(messages)
            self.main.win.getch()
            sys.exit(1)

    def print_and_wait(self, messages, offset=5, spacing=2):
        self.main.show()
        for message in messages:
            offset = offset + spacing
            offset = offset + self.main.addstr_centre(offset, message)
        self.main.win.getch()


class JetsonIO(object):
    def __init__(self, stdscreen):
        height = 40
        width = 80
        curses.resizeterm(height, width)
        self.win = MainWindow(stdscreen, height - 2, width - 10)

        try:
            self.menu = MainMenu(stdscreen, self.win, height - 4, width - 12)
            self.menu.show()
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as error:
            messages = []
            messages.append("FATAL ERROR!")
            messages.append(str(error))
            messages.append("Press any key to terminate")
            self.win.print_and_wait(messages)
            sys.exit(1)


if __name__ == '__main__':
    curses.wrapper(JetsonIO)
