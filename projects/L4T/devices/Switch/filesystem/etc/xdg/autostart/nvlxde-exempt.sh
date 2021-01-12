#!/bin/bash
#
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
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

set -e

app_dir="/home/${USER}/.local/share/applications"
reboot="/usr/share/applications/reboot.desktop"
logout="/usr/share/applications/logout.desktop"
shutdown="/usr/share/applications/shutdown.desktop"
lens="/usr/share/applications/unity-lens-photos.desktop"

if [ ! -d "${app_dir}" ]; then
	mkdir -p "${app_dir}"
fi

# It's important that we check all desktop application files whether
# they are present in the system and not copied to the user's local
# path.
if [ -f "${reboot}" ] && [ ! -f "${app_dir}/reboot.desktop" ]; then
	cp "${reboot}" "${app_dir}"
	sed -i '/^NotShowIn=/ s/$/LXDE;/' "${app_dir}/reboot.desktop"
fi

if [ -f "${logout}" ] && [ ! -f "${app_dir}/logout.desktop" ]; then
	cp "${logout}" "${app_dir}"
	sed -i '/^NotShowIn=/ s/$/LXDE;/' "${app_dir}/logout.desktop"
fi

if [ -f "${shutdown}" ] && [ ! -f "${app_dir}/shutdown.desktop" ]; then
	cp "${shutdown}" "${app_dir}"
	sed -i '/^NotShowIn=/ s/$/LXDE;/' "${app_dir}/shutdown.desktop"
fi

if [ -f "${lens}" ] && [ ! -f "${app_dir}/unity-lens-photos.desktop" ]; then
	cp "${lens}" "${app_dir}"
	sed -i -e '$aNotShowIn=LXDE' "${app_dir}/unity-lens-photos.desktop"
fi
