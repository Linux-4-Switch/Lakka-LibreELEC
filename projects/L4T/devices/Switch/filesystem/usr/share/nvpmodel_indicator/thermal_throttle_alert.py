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

from pathlib import Path
import multiprocessing as mp
import time

class ThermalCommon(object):
    def __init__(self, path):
        self.path = path
        self.type = self.get_type(path)

    @staticmethod
    def get_type(path):
        return Path(path).joinpath('type').read_text().strip()

class ThermalZone(ThermalCommon):
    def __init__(self, path):
        super().__init__(path)

class MonitoredZone(ThermalZone):
    def __init__(self, path, alert_cdev):
        super().__init__(path)
        self.alert_cdev = UserspaceAlert(alert_cdev)

    def wait_alert(self):
        self.alert_cdev.read_alert()

class CoolingDevice(ThermalCommon):
    def __init__(self, path):
        super().__init__(path)

    def cur_state(self):
        return Path(self.path).joinpath('cur_state').read_text().strip()

class UserspaceAlert(CoolingDevice):
    def __init__(self, path):
        super().__init__(path)

    def read_alert(self):
        return self.path.joinpath('userspace_alert/thermal_alert_block').read_text().strip()

class ThermalThrottleAlert(object):
    def __init__(self, alert_type):
        tz_paths = [p for p in Path('/sys/class/thermal').glob(f'thermal_zone*')]
        user_alert_paths = [p for tz in tz_paths for p in Path(tz).glob(f'cdev[0-9]') if alert_type in CoolingDevice.get_type(p)]
        self.alert_type = alert_type
        self.monitored_zones = [MonitoredZone(p.parent, p) for p in user_alert_paths]
        self.q = mp.Queue()
        self.processes = [mp.Process(target=self.__event_monitor, args=(self.q, z)) for z in self.monitored_zones]
        for p in self.processes:
            p.daemon = True
            p.start()

    def __event_monitor(self, queue, zone):
        while True:
            MonitoredZone.wait_alert(zone)
            queue.put((self.alert_type, zone.type))
            time.sleep(1)

    def wait_event(self):
        return self.q.get()

if __name__ == '__main__':
    def alert_test(alert_type):
        alert = ThermalThrottleAlert(alert_type)
        print(f"{alert_type}: {[z.type for z in alert.monitored_zones]} Alert devices: {[z.alert_cdev.path for z in alert.monitored_zones]}")
        print("Waiting for thermal throttle event..")
        while True:
            event = alert.wait_event()
            print(f"{alert_type} event: {event}")

    alert_types = ['throttle-alert', 'hot-surface']
    children = [mp.Process(target=alert_test, args=(t,)) for t in alert_types]

    for child in children:
        child.start()

    for child in children:
        child.join()
