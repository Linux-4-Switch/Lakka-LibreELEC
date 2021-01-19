#!/bin/bash

#
# Copyright (c) 2016-2020, NVIDIA CORPORATION.  All rights reserved.
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

if [ ! -e /etc/nv/nvfirstboot ]; then
	exit 0
fi

if [ -f "/usr/share/applications/ubuntu-amazon-default.desktop" ]; then
	echo "Hidden=true" >> /usr/share/applications/ubuntu-amazon-default.desktop
fi

# Generate SSH host keys if they are not present under /etc/ssh/
if [ -e "/lib/systemd/system/ssh.service" ]; then
	# Wait for the process to finish which has aquired this lock
	while fuser "/var/cache/debconf/config.dat" > "/dev/null" 2>&1; do sleep 1; done;
	while fuser "/var/cache/debconf/templates.dat" > "/dev/null" 2>&1; do sleep 1; done;
	while fuser "/var/cache/debconf/passwords.dat" > "/dev/null" 2>&1; do sleep 1; done;
	while [ ${status-1} -ne 0 ]; do
		dpkg-reconfigure --frontend=noninteractive openssh-server; status="$?"
	done
fi

# Update chipid to apt source list file
SOURCE="/etc/apt/sources.list.d/nvidia-l4t-apt-source.list"
if [ -e "${SOURCE}" ]; then
	CHIP="$(cat /proc/device-tree/compatible)"
	if [[ "${CHIP}" =~ "tegra210" ]]; then
		sed -i "s/<SOC>/t210/g" "${SOURCE}"
	elif [[ "${CHIP}" =~ "tegra186" ]]; then
		sed -i "s/<SOC>/t186/g" "${SOURCE}"
	elif [[ "${CHIP}" =~ "tegra194" ]]; then
		sed -i "s/<SOC>/t194/g" "${SOURCE}"
	else
		logger "nvfb: Updating apt source list failed with exit code: 1"
	fi
fi

# Reconfigure blueman if it's present in rootfs
if [ -d "/usr/lib/blueman" ]; then
	dpkg-reconfigure blueman
fi

# Restrict blueman applet loading at login
blueman_app="/etc/xdg/autostart/blueman.desktop"
if [ -f "${blueman_app}" ]; then
	sed -i '/^NotShowIn=/ s/$/;Unity;GNOME/' "${blueman_app}"
fi

rm -rf /etc/nv/nvfirstboot
