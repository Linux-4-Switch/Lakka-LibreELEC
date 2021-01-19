#!/bin/bash

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

DISPLAY_PLUGGED="$(cat /sys/class/graphics/fb*/device/panel_connected)"
CHIP="$(cat /proc/device-tree/compatible)"
/bin/systemctl start nv-l4t-usb-device-mode.service

if [[ -f /usr/lib/nvidia/resizefs/nvresizefs.templates ]]; then
	/usr/bin/debconf-loadtemplate nvresizefs \
		/usr/lib/nvidia/resizefs/nvresizefs.templates
fi

if [[ -f /usr/lib/nvidia/swap/nvswap.templates ]]; then
	/usr/bin/debconf-loadtemplate nvswap \
		/usr/lib/nvidia/swap/nvswap.templates
fi

# Wait for the process to finish which has aquired this lock
while fuser "/var/cache/debconf/config.dat" > "/dev/null" 2>&1; do sleep 1; done;
while fuser "/var/cache/debconf/templates.dat" > "/dev/null" 2>&1; do sleep 1; done;

if [[ "${DISPLAY_PLUGGED}" =~ "1" ]]; then
	/bin/echo "Please complete system configuration setup on desktop to proceed..." > "/dev/kmsg"
	/bin/systemctl start nv-oem-config-gui.service
else
	CONF_FILE=""
	DEFAULT_UART_PORT=""
	if [[ "${CHIP}" =~ "tegra194" ]]; then
		CONF_FILE="/etc/nv-oem-config.conf.t194"
		DEFAULT_UART_PORT="ttyTCU0"
	elif [[ "${CHIP}" =~ "tegra186" ]]; then
		CONF_FILE="/etc/nv-oem-config.conf.t186"
		DEFAULT_UART_PORT="ttyS0"
	elif [[ "${CHIP}" =~ "tegra210" ]]; then
		CONF_FILE="/etc/nv-oem-config.conf.t210"
		DEFAULT_UART_PORT="ttyS0"
	fi

	if [[ -n "${CONF_FILE}" && -n "${DEFAULT_UART_PORT}" ]]; then
		UART_PORT="$(grep uart-port "${CONF_FILE}" | cut -d '=' -f 2)"
		if [[ -n "${UART_PORT}" ]]; then
			for i in {1..5}; do
				if [[ -e "/dev/${UART_PORT}" ]]; then
					break;
				elif [[ "${i}" =~ "5" ]]; then
					/bin/echo "/dev/${UART_PORT} is invalid, change system \
configuration setup on /dev/${DEFAULT_UART_PORT}" > "/dev/kmsg"
					UART_PORT="${DEFAULT_UART_PORT}"
				else
					sleep 1
				fi
			done

			if [[ "${UART_PORT}" =~ "ttyGS0" ]]; then
				/bin/echo "Please complete system configuration setup on the \
serial port provided by Jetson's USB device mode connection. e.g. /dev/ttyACMx where x can 0,\
 1, 2 etc." > "/dev/kmsg"
			else
				/bin/echo "Please complete system configuration setup on the \
serial port. e.g. /dev/ttyUSBx where can x 0, 1, 2 etc." > "/dev/kmsg"
			fi
			/bin/stty -F /dev/${UART_PORT} 115200 cs8 -parenb -cstopb
			/bin/systemctl start nv-oem-config-debconf@${UART_PORT}.service
		fi
	fi
fi
exit 0
