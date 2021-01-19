#!/usr/bin/env python3
#
# Copyright (c) 2020, NVIDIA CORPORATION.  All Rights Reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import re
import time
import threading

def oc_event_t210():
    evt_cnt = None
    regex = re.compile(" *(\d+): +(\d+).*soctherm_edp.*")
    while True:
        for line in open("/proc/interrupts"):
            m = regex.match(line)
            if m != None:
                break
        if evt_cnt != m.group(2):
            if evt_cnt:
                return ('throttle-alert', 'Over-current')
            evt_cnt = m.group(2)
        time.sleep(1)

def oc_event_t186():
    while True:
        time.sleep(threading.TIMEOUT_MAX)

oc_event_func = {}
oc_event_func['tegra210'] = oc_event_t210
oc_event_func['tegra186'] = oc_event_t186
oc_event_func['tegra194'] = oc_event_t186

def soc_family():
    try:
        with open("/proc/device-tree/compatible") as f:
            compatible = f.read().split('\x00')
            for s in compatible:
                for soc in oc_event_func.keys():
                    if soc in s:
                        soc_family = soc
            return soc_family
    except IOError:
            return 'unknown'

class OcEvent(object):
    def __init__(self):
        self.wait_event = oc_event_func[soc_family()]

    def wait_event():
        return self.wait_event()

if __name__ == '__main__':
    print(f"SoC family: {soc_family()}")
    print("Waiting for OC event..")
    oc = OcEvent()
    oc.wait_event()
    print("OC event occurred.")
