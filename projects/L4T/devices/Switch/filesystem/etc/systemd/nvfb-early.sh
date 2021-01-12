#!/bin/bash

#
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

if [ ! -e /etc/nv/nvfirstboot ]; then
	exit 0
fi

ARCH=`/usr/bin/dpkg --print-architecture`
if [ "${ARCH}" = "arm64" ]; then
	echo "/usr/lib/aarch64-linux-gnu/tegra" > \
		/etc/ld.so.conf.d/nvidia-tegra.conf
	echo "/usr/lib/aarch64-linux-gnu/tegra-egl" > \
		/usr/lib/aarch64-linux-gnu/tegra-egl/ld.so.conf
	echo "/usr/lib/aarch64-linux-gnu/tegra" > \
		/usr/lib/aarch64-linux-gnu/tegra/ld.so.conf
	update-alternatives \
		--install /etc/ld.so.conf.d/aarch64-linux-gnu_EGL.conf \
		aarch64-linux-gnu_egl_conf \
		/usr/lib/aarch64-linux-gnu/tegra-egl/ld.so.conf 1000
	update-alternatives \
		--install /etc/ld.so.conf.d/aarch64-linux-gnu_GL.conf \
		aarch64-linux-gnu_gl_conf \
		/usr/lib/aarch64-linux-gnu/tegra/ld.so.conf 1000
fi

ldconfig

# Read total memory size in gigabyte
TOTAL_MEM=$(free --giga | awk '/^Mem:/{print $2}')
if [ $? -eq 0 ]; then
	# If RAM size is less than 4 GB, set default display manager as LightDM
	if [ -e "/lib/systemd/system/lightdm.service" ] &&
		[ "${TOTAL_MEM}" -lt 4 ]; then
		DEFAULT_DM=$(cat "/etc/X11/default-display-manager")
		if [ "${DEFAULT_DM}" != "/usr/sbin/lightdm" ]; then
			echo "/usr/sbin/lightdm" > "/etc/X11/default-display-manager"
			DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true dpkg-reconfigure lightdm
			echo set shared/default-x-display-manager lightdm | debconf-communicate
		fi
	fi
else
	echo "ERROR: Cannot get total memory size."
fi

# Allow anybody to run X
if [ -f "/etc/X11/Xwrapper.config" ]; then
	sed -i 's/allowed_users.*/allowed_users=anybody/' "/etc/X11/Xwrapper.config"
fi
