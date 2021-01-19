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


# Minimum available memory limit (in MB)
threshold=150

# Check time interval (in sec)
interval=300

mem_warning()
{
	while : ; do
		available="$(free -m | awk '/Mem:/{print $7}')"

		if [ "${available}" -lt "${threshold}" ]; then
			free_mem="$(free -m|awk '/^Mem:/{print $4}')"
			buffers="$(free -m|awk '/^Mem:/{print $6}')"
			message="Memory available for new process: ${available} MB\n"
			message="${message} free ${free_mem} MB, buffers/cache ${buffers} MB"
			xusers=($(who|grep -E "\(:[0-9](\.[0-9])*\)"|awk '{print $1$5}'|sort -u))
			for xuser in "${xusers}"; do
			    name=(${xuser/(/ })
			    display=${name[1]/)/}
			    dbus_address=unix:path=/run/user/$(id -u ${name[0]})/bus
			    sudo -u "${name[0]}" display="${display}" \
				    DBUS_SESSION_BUS_ADDRESS="${dbus_address}" PATH="${PATH}" \
				    notify-send "Low Memory Warning" "${message}"
			done
		fi
		sleep "${interval}"
	done
}

# Read Total memory size
total_mem=$(free -g|awk '/^Mem:/{print $2}')

# If RAM size is less than 8 GB, mem_warning will be invoked
if [ "${total_mem}" -lt 8 ]; then
	mem_warning
fi
