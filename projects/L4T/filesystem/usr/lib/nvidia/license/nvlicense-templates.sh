#!/bin/bash

# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

license_file="/usr/share/doc/nvidia-tegra/L4T_End_User_License_Agreement.txt"
templates_file="/usr/lib/nvidia/license/nvlicense.templates"

cat > "${templates_file}" << ENDOFHERE
Template: ubiquity/text/nvlicense_heading_label
Type: text
Description: License For Customer Use of NVIDIA Software

Template: nvlicense/welcome
Type: text
Description: Welcome to Jetson Initial Configuration

Template: nvlicense/eula
Type: note
ENDOFHERE

if [ ! -f "${license_file}" ] && [ -f "${license_file}.gz" ]; then
	cp "${license_file}.gz" /tmp
	license_file="/tmp/$(basename "${license_file}")"
	gunzip "${license_file}.gz"
fi

# Read license content from text file
exec < "${license_file}"

# Capture the first line as description
while read line; do
	if [ -n "${line}" ]; then
		echo "Description: ${line}" >> "${templates_file}"
		break
	fi
done

# Search the second line (ignore blank line) as beginning of
# extend description
skip="true"
while read line; do
	if [ -z "${line}" ]; then
		if [ "${skip}" = "true" ]; then
			continue
		else
			# Replace all blank line with '.'
			line="."
		fi
	fi
	skip="false"
	# Append a space in beginning of each line
	echo " ${line}" >> "${templates_file}"
done
