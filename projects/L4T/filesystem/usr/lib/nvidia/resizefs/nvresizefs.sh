#!/bin/bash

# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
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
	echo "	-h | --help"
	echo "		Show this usage"
	echo ""
	echo "	-c | --check"
	echo "		Check whether ${script_name} can be used on current platform"
	echo ""
	echo "	-g | --get"
	echo "		Show APP partition size in MB"
	echo ""
	echo "	-m | --max"
	echo "		Show APP partition maximum available size in MB"
	echo ""
	echo "	-s <app_size> | --size <app_size>"
	echo "		Set APP partition size in MB"
	echo ""
	echo "Without any option means consume all unallocated"
	echo "space on SD card."
	echo ""
	echo "Example:"
	echo "${script_name}"
	echo "${script_name} -s 16384"
}

function check_pre_req()
{
	root_dev="$(sed -ne 's/.*\broot=\([^ ]*\)\b.*/\1/p' < /proc/cmdline)"

	if [[ "${root_dev}" == *UUID* ]]; then
		root_dev="$(/sbin/findfs ${root_dev})"
	fi

	if [[ "${root_dev}" == /dev/mmcblk* ]] || [[ "${root_dev}" == /dev/sd* ]]; then
		block_dev="$(/bin/lsblk -no pkname ${root_dev})"
		root_dev="$(echo $root_dev | sed 's/^.....//g')"
	fi

	if [ "${block_dev}" != "" ]; then
		# Check whether APP partition is located at the end of the disk
		root_start_sector="$(cat /sys/block/${block_dev}/${root_dev}/start)"
		all_start_sectors="$(cat /sys/block/${block_dev}/*/start)"

		is_last="true"
		for start_sector in ${all_start_sectors}; do
			if [[ "${start_sector}" -gt "${root_start_sector}" ]]; then
				is_last="false"
				break
			fi
		done
		support_resizefs="${is_last}"
	fi
}

function get_app_size()
{
	partition_size="$(cat /sys/block/${block_dev}/${root_dev}/size)"
	echo "$((partition_size/2/1024))"
}

function max_available_app_size()
{
	# Move backup GPT header to end of disk
	sgdisk --move-second-header "/dev/${block_dev}" > /dev/null 2>&1
	app_start_sector="$(cat /sys/block/${block_dev}/${root_dev}/start)"
	last_usable_sector="$(sgdisk -p /dev/${block_dev} | \
				grep "last usable sector" | \
				awk '{print $10}')"

	echo "$(((last_usable_sector - app_start_sector + 1)/2/1024))"
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
			echo "${support_resizefs}"
			exit 0
			;;
		-g | --get)
			if [ "${support_resizefs}" = "false" ]; then
				echo "ERROR: ${script_name} doesn't support this platform."
				exit 1
			fi
			get_app_size
			exit 0
			;;
		-m | --max)
			if [ "${support_resizefs}" = "false" ]; then
				echo "ERROR: ${script_name} doesn't support this platform."
				exit 1
			fi
			max_available_app_size
			exit 0
			;;
		-s | --size)
			[ -n "${2}" ] || usage "Not enough parameters"
			size="+${2}M"
			shift 2
			;;
		*)
			usage "Unknown option: ${1}"
			exit 1
			;;
		esac
	done
}

script_name="$(basename "${0}")"
support_resizefs="false"
size="0"
root_dev=""
block_dev=""

check_pre_req
parse_args "${@}"

if [ "${support_resizefs}" = "false" ]; then
	echo "ERROR: ${script_name} doesn't support this platform."
	exit 1
fi

# Move backup GPT header to end of disk
sgdisk --move-second-header "/dev/${block_dev}"

# Get partition information for root partition
partition_num="$(cat /sys/block/${block_dev}/${root_dev}/partition)"
partition_name="$(sgdisk -i ${partition_num} /dev/${block_dev} | \
	grep "Partition name" | cut -d\' -f2)"

partition_type="$(sgdisk -i ${partition_num} /dev/${block_dev} | \
	grep "Partition GUID code:" | cut -d' ' -f4)"

partition_uuid="$(sgdisk -i ${partition_num} /dev/${block_dev} | \
	grep "Partition unique GUID:" | cut -d' ' -f4)"

partition_attr="$(sgdisk -i ${partition_num} /dev/${block_dev} | \
	grep "Attribute flags:" | cut -d' ' -f3)"

# Get start sector of the root partition
start_sector="$(cat /sys/block/${block_dev}/${root_dev}/start)"

# Delete and re-create the root partition
# This will resize the root partition.
sgdisk -d "${partition_num}" \
	-n "${partition_num}":"${start_sector}":"${size}" \
	-c "${partition_num}":"${partition_name}" \
	-t "${partition_num}":"${partition_type}" \
	-u "${partition_num}":"${partition_uuid}" \
	-A "${partition_num}":=:"${partition_attr}" \
	"/dev/${block_dev}"

# Inform kernel and OS about change in partition table and root
# partition size
partprobe "/dev/${block_dev}"

# Resize filesystem on root partition to consume all un-allocated
# space on disk
resize2fs "/dev/${root_dev}"
