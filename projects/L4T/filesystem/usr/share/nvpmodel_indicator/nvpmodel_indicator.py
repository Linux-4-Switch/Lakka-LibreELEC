#!/usr/bin/env python3
#
# Copyright (c) 2019-2020, NVIDIA CORPORATION.  All Rights Reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import signal
import gi
import nvpmodel as nvpm
import thermal_throttle_alert as thermal
import over_current as oc
import subprocess
import time
import threading
import re
import sys
import multiprocessing as mp

gi.require_version("Gtk", "3.0")
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GObject

INDICATOR_ID = 'nvpmodel'
ICON_DEFAULT = os.path.abspath('/usr/share/nvpmodel_indicator/nv_logo.svg')
ICON_WARNING = 'dialog-warning'

THROTTLE_ALERT = 'throttle-alert'
HOT_SURFACE_ALERT = 'hot-surface-alert'

notify_disable = False
thermal_events = {}
evt_queue = mp.Queue()

def pm_update_active(item):
    cur_mode = pm.cur_mode()
    menu = item.get_submenu()
    for child in menu.get_children():
        if child.get_label()[0] == cur_mode:
            child.set_active(True)

def confirm_reboot():
    dialog = gtk.MessageDialog(None, 0, gtk.MessageType.WARNING,
        gtk.ButtonsType.OK_CANCEL, "System reboot is required to apply changes")
    dialog.set_title("WARNING")
    dialog.format_secondary_text( "Do you want to reboot NOW?")
    response = dialog.run()
    dialog.destroy()
    return response == gtk.ResponseType.OK

def set_power_mode(item, mode_id):
    if item.get_active() and mode_id != pm.cur_mode():
        success = pm.set_mode(mode_id, ['pkexec'])
        if not success and confirm_reboot():
            pm.set_mode(mode_id, ['pkexec'], force=True)
            return
        indicator.set_label(pm.get_name_by_id(pm.cur_mode()), INDICATOR_ID)

def do_tegrastats(_):
    cmd = "x-terminal-emulator -e pkexec tegrastats".split()
    subprocess.call(cmd)

def clear_warning():
    indicator.set_icon(ICON_DEFAULT)
    item_throttle_evt.set_sensitive(False)
    thermal_events.clear()

def disable_notification(self):
    global notify_disable
    notify_disable = self.get_active()
    if notify_disable and indicator.get_icon() == ICON_WARNING:
        clear_warning()

def quit(_):
    running.clear()
    evt_queue.put(None)
    gtk.main_quit()

def build_warning_msg(evt):
    evt_sorted = sorted(evt)
    throttle_events = [e.replace('throttle-', '') for e in evt_sorted if 'throttle-' in e]
    device_is_hot = 'hot-surface-alert' in evt_sorted

    msg_lines = []
    if device_is_hot:
        msg_lines.append(f"Caution - Hot surface. Do Not Touch.")
    if throttle_events:
        msg_lines.append(f"System throttled due to {', '.join(throttle_events)}.")
    msg = '\n'.join(msg_lines)
    return msg

def ack_warning(*args):
    ack = gtk.MessageDialog(None, 0, gtk.MessageType.WARNING,
        gtk.ButtonsType.CLOSE, build_warning_msg(thermal_events))
    ack.set_title("WARNING")
    ack.format_secondary_text("")
    ack.run()
    ack.destroy()
    clear_warning()

def build_menu():
    global item_throttle_evt

    menu = gtk.Menu()
    item_pm = gtk.MenuItem('Power mode')
    item_pm.connect('activate', pm_update_active)
    menu.append(item_pm)

    submenu = gtk.Menu()
    group = []
    for mode in pm.power_modes():
        label = mode.id + ': ' + mode.name
        item_mode = gtk.RadioMenuItem.new_with_label(group, label)
        group = item_mode.get_group()
        item_mode.connect('activate', set_power_mode, mode.id)
        submenu.append(item_mode)
    item_pm.set_submenu(submenu)

    item_tstats = gtk.MenuItem('Run tegrastats')
    item_tstats.connect('activate', do_tegrastats)
    menu.append(item_tstats)

    item_throttle_evt = gtk.MenuItem('Acknowledge warning')
    item_throttle_evt.set_sensitive(False)
    item_throttle_evt.connect('activate', ack_warning)
    menu.append(item_throttle_evt)

    menu_options = gtk.Menu()
    item_setting = gtk.MenuItem('Settings')
    item_setting.set_submenu(menu_options)
    menu.append(item_setting)

    item_notify_dis = gtk.CheckMenuItem('Disable notification')
    item_notify_dis.connect('toggled', disable_notification)
    menu_options.append(item_notify_dis)

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)

    menu.show_all()
    return menu

def do_warning(evt):
    if notify_disable:
        return
    indicator.set_icon(ICON_WARNING)
    item_throttle_evt.set_sensitive(True)
    warning.update(build_warning_msg(evt))
    warning.show()

def mode_change_monitor(running):
    cur_mode = pm.cur_mode()
    while running.is_set():
        if cur_mode != pm.cur_mode():
            cur_mode = pm.cur_mode()
            # Let main thread do GUI things otherwise there can be
            # conflicts.
            GObject.idle_add(
                indicator.set_label,
                pm.get_name_by_id(cur_mode), INDICATOR_ID,
                priority=GObject.PRIORITY_DEFAULT)
        time.sleep(1)

def wait_event(queue, event):
    while True:
        queue.put(event.wait_event())

def evt_monitor(running):
    events = [oc.OcEvent(), thermal.ThermalThrottleAlert(THROTTLE_ALERT), thermal.ThermalThrottleAlert(HOT_SURFACE_ALERT)]
    monitors = [mp.Process(target=wait_event, args=(evt_queue, evt)) for evt in events]
    new_events = {}
    last_shown = 0.

    for p in monitors:
        p.daemon = True
        p.start()

    while running.is_set():
        evt = evt_queue.get()
        if evt is None:
            continue
        if THROTTLE_ALERT in evt[0]:
            new_events['throttle-' + evt[1]] = True
        elif HOT_SURFACE_ALERT in evt[0]:
            new_events[evt[0]] = True
        thermal_events.update(new_events)
        now = time.monotonic()
        if now - last_shown < 1:
            continue
        last_shown = now
        do_warning(new_events)
        new_events.clear()


pm = nvpm.nvpmodel()

# Unity panel strips underscore from indicator's label, replace '_' with
# space here so that name of power modes will be more readable.
for mode in pm.power_modes():
    mode.name = mode.name.replace('_', ' ')

# AppIndicator3 doesn't handle SIGINT, wire it up.
signal.signal(signal.SIGINT, signal.SIG_DFL)

notify.init(INDICATOR_ID)
warning = notify.Notification()

indicator = appindicator.Indicator.new(INDICATOR_ID, ICON_DEFAULT,
    appindicator.IndicatorCategory.SYSTEM_SERVICES)
indicator.set_label(pm.get_name_by_id(pm.cur_mode()), INDICATOR_ID)
indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
indicator.set_menu(build_menu())

running = threading.Event()
running.set()
threading.Thread(target=evt_monitor, args=[running]).start()
threading.Thread(target=mode_change_monitor, args=[running]).start()

gtk.main()
