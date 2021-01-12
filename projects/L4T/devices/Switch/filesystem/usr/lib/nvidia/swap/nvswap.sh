#!/bin/bash

# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
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

# This is a script to resize partition and filesystem on the root partition
# This will consume all un-allocated sapce on SD card after boot.

set -e

function usage()
{
	if [ -n "${1}" ]; then
		echo "${1}"
	fi

	echo "Usage:"
	echo "${script_name} [options]"
	echo ""
	echo "Available options are:"
	echo ""
	echo "  -h | --help"
	echo "          Show this usage"
	echo ""
	echo "  -c | --check"
	echo "          Check whether ${script_name} can be used on current platform"
	echo ""
	echo "  -s | --swap"
	echo "          Create SWAP File (Size 4GB)"
	echo ""
	echo "Example:"
	echo "${script_name} -s"
}

function create_swap()
{
	root_dev="$(sed -ne 's/.*\broot=\([^ ]*\)\b.*/\1/p' < /proc/cmdline)"
	if [[ "${root_dev}" == *UUID* ]]; then
		root_dev="$(/sbin/findfs ${root_dev})"
	fi

	tmem=$(df -H | awk -v var="${root_dev}" '$1 ~ var' | awk '{print $2}')
	amem=$(df -H | awk -v var="${root_dev}" '$1 ~ var' | awk '{print $4}')
	tmem="${tmem::-1}"
	tmem=${tmem%.*}
	amem="${amem::-1}"
	amem=${amem%.*}

	# Make sure the total capacity of the SD/EMMC is more than 16G and
	# available memory on SD/EMMC is more than 4G
	if [ "${tmem}" -gt 16 ] && [ "${amem}" -gt 4 ]; then
		fallocate -l 4G /swapfile
		chmod 600 /swapfile
		mkswap /swapfile
		swapon /swapfile

		fstab_file="/etc/fstab"

		if [ ! -f "${fstab_file}" ]; then
			touch "${fstab_file}"
		fi
		sed -i -e '$a/swapfile            swap                  swap           defaults                                     0 0' ${fstab_file}
	fi
}

function disable_zram()
{
	zfile="/etc/systemd/system/multi-user.target.wants/nvzramconfig.service"
	if [ -L "${zfile}" ]; then
		"rm" "-f" "${zfile}"
	fi
}

function parse_args()
{
	while [ -n "${1}" ]; do
		case "${1}" in
		-h | --help)
			usage
			exit 0
			;;
		-c | --check)
			# make sure that memory is less than 4G
			mem=$(free --mega | awk '/^Mem:/{print $2}')
			mem=$(echo "scale=1;$mem/1000" | bc)
			mem=$(echo "${mem}" | awk '{print int($1+0.5)}')
			if [ "${mem}" -lt 4 ]; then
				echo "true"
			else
				echo "false"
			fi
			exit 0
			;;
		-s | --swap)
			create_swap
			exit 0
			;;
		*)
			usage "Unknown option: ${1}"
			exit 1
		;;
		esac
	done
}

script_name="$(basename "${0}")"
parse_args "${@}"

