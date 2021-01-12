#!/bin/bash
# Copyright (c) 2019-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# This script runs on target to check if need to update QSPI partitions for Nano
# If the running system version match the bootloader debian package,
# then check the VER in QSPI, if the VER is less then running system version,
# install the package to update QSPI.

BOOT_CTRL_CONF="/etc/nv_boot_control.conf"
T210REF_UPDATER="/usr/sbin/l4t_payload_updater_t210"
T186REF_UPDATER="/usr/sbin/nv_bootloader_payload_updater"
PACKAGE_DIR="/opt/nvidia/l4t-packages/bootloader"
PACKAGE_NAME="nvidia-l4t-bootloader"

# When create image, user may flash device with symlik board
# config name or orignal name, so the nv_boot_control.conf
# may have different board name informaton.
# Unify it to "jetson-*"
update_boot_ctrl_conf() {
	local update_str=""

	if [[ "${tnspec}" == *"p3448-0000-emmc"* ]]; then
		# "jetson-nano-emmc" for "p3448-0000-emmc"
		update_str="s/p3448-0000-emmc/jetson-nano-emmc/g";
	elif [[ "${tnspec}" == *"p3448-0000-sd"* ]]; then
		# "jetson-nano-qspi-sd" for "p3448-0000-sd"
		update_str="s/p3448-0000-sd/jetson-nano-qspi-sd/g";
	elif [[ "${tnspec}" == *"p3448-0000"* ]]; then
		# "jetson-nano-qspi" for "p3448-0000"
		update_str="s/p3448-0000/jetson-nano-qspi/g";
	elif [[ "${tnspec}" == *"p2371-2180-devkit"* ]]; then
		# "jetson-tx1" for "p2371-2180-devkit"
		update_str="s/p2371-2180-devkit/jetson-tx1/g";
	elif [[ "${tnspec}" == *"p2771-0000-devkit"* ]]; then
		# "jetson-tx2" for "p2771-0000-devkit"
		update_str="s/p2771-0000-devkit/jetson-tx2/g";
	elif [[ "${tnspec}" == *"p2771-3489-ucm1"* ]]; then
		# "jetson-tx2i" for "p2771-3489-ucm1"
		update_str="s/p2771-3489-ucm1/jetson-tx2i/g";
	elif [[ "${tnspec}" == *"p2771-0000-0888"* ]]; then
		# "jetson-tx2-4GB" for "p2771-0000-0888"
		update_str="s/p2771-0000-0888/jetson-tx2-4GB/g";
	elif [[ "${tnspec}" == *"p2771-0000-as-0888"* ]]; then
		# "jetson-tx2-as-4GB" for "p2771-0000-as-0888"
		update_str="s/p2771-0000-as-0888/jetson-tx2-as-4GB/g";
	elif [[ "${tnspec}" == *"p2972-0000-devkit-maxn"* ]]; then
		# "jetson-xavier-maxn" for "p2972-0000-devkit-maxn"
		update_str="s/p2972-0000-devkit-maxn/jetson-xavier-maxn/g";
	elif [[ "${tnspec}" == *"p2972-0000-devkit-slvs-ec"* ]]; then
		# "jetson-xavier-slvs-ec" for "p2972-0000-devkit-slvs-ec"
		update_str="s/p2972-0000-devkit-slvs-ec/jetson-xavier-slvs-ec/g";
	elif [[ "${tnspec}" == *"p2972-0000-devkit"* ]]; then
		# "jetson-xavier" for "p2972-0000-devkit"
		update_str="s/p2972-0000-devkit/jetson-xavier/g";
	elif [[ "${tnspec}" == *"p2972-0006-devkit"* ]]; then
		# "jetson-xavier-8gb" for "p2972-0006-devkit"
		update_str="s/p2972-0006-devkit/jetson-xavier-8gb/g";
	elif [[ "${tnspec}" == *"p2972-as-galen-8gb"* ]]; then
		# "jetson-xavier-as-8gb" for "p2972-as-galen-8gb"
		update_str="s/p2972-as-galen-8gb/jetson-xavier-as-8gb/g";
	elif [[ "${tnspec}" == *"p2822+p2888-0001-as-p3668-0001"* ]]; then
		# "jetson-xavier-as-xavier-nx" for "p2822+p2888-0001-as-p3668-0001"
		update_str="s/p2822+p2888-0001-as-p3668-0001/jetson-xavier-as-xavier-nx/g";
	elif [[ "${tnspec}" == *"p3509-0000+p3668-0000-qspi-sd"* ]]; then
		# jetson-xavier-nx-devkit.conf ->p3509-0000+p3668-0000-qspi-sd.conf
		update_str="s/p3509-0000+p3668-0000-qspi-sd/jetson-xavier-nx-devkit/g";
	elif [[ "${tnspec}" == *"p3509-0000+p3668-0001-qspi-emmc"* ]]; then
		# jetson-xavier-nx-devkit-emmc.conf -> p3509-0000+p3668-0001-qspi-emmc.conf
		update_str="s/p3509-0000+p3668-0001-qspi-emmc/jetson-xavier-nx-devkit-emmc/g";
	fi

	if [[ "${update_str}" != "" ]]; then
		sed -i "${update_str}" "${BOOT_CTRL_CONF}";
	fi
}

sys_rel=""
sys_maj_ver=""
sys_min_ver=""

read_sys_ver() {
	# 1. get installed bootloader package's version
	# sample: ii  nvidia-l4t-bootloader  32.2.0-20190514154120  arm64  NVIDIA Bootloader Package
	# installed_deb_ver=32.2.0-20190514154120
	installed_deb_ver="$(dpkg -l | grep "${PACKAGE_NAME}" | awk '/'${PACKAGE_NAME}'/ {print $3}')"
	if [ "${installed_deb_ver}" == "" ]; then
		exit 0
	fi

	# 2. get main deb_version
	deb_version="$(echo "${installed_deb_ver}" | cut -d "-" -f 1)"

	# 3. use deb_version as sys_version
	# sample: sys_rel=32, sys_maj_ver=2, sys_min_ver=0
	sys_rel="$(echo "${deb_version}" | cut -d "." -f 1)"
	sys_maj_ver="$(echo "${deb_version}" | cut -d "." -f 2)"
	sys_min_ver="$(echo "${deb_version}" | cut -d "." -f 3)"
}

ver_info=""
qspi_rel=""
qspi_maj_ver=""
qspi_min_ver=""

# read t210ref VER partition to get QSPI version
read_t210ref_qspi_ver_info() {
	ver_info="$(${T210REF_UPDATER} -v)"
}

# read t186ref VER partition to get QSPI version
read_t186ref_qspi_ver_info() {
	ver_info="$(${T186REF_UPDATER} --print-ver)"
}

# parse version info
parse_qspi_ver_info() {
	local ver_line=""
	local info=""
	local rel_number=""
	local version=""

	# version sample:
	# Version:
	# NV3
	# # R32 , REVISION: 4.0
	# BOARDID=xxxx BOARDSKU=yyy FAB=zzz

	ver_line=$(echo "${ver_info}" | sed -n '/Version:/'=)
	((ver_line++))
	info=$(echo "${ver_info}" | sed -n "${ver_line}p")

	if [[ "${info}" == "NV1" ]]; then
		qspi_rel=31
		qspi_maj_ver=0
		qspi_min_ver=0
	elif [[ "${info}" == *"NV"* ]]; then
		((ver_line++))
		ver_info=$(echo "${ver_info}" | sed -n "${ver_line}p")

		rel_number="$(echo "${ver_info}" | awk '/#/ {print $2}')"
		qspi_rel="$(echo "${rel_number}" | sed 's/R//')"

		version=$(echo "${ver_info}" | awk '/#/ {print $5}')
		version="$(echo "${version}" | sed 's/,//')"

		qspi_maj_ver="$(echo "${version}" | cut -d "." -f 1)"
		qspi_min_ver="$(echo "${version}" | cut -d "." -f 2)"
	else
		echo "Error. Cannot get valid version information"
		echo "Exiting ..."
		exit 1
	fi
}

# check qspi version, if need update it.
# return:  0: needs update; 1: doesn't need update.
update_qspi_check () {
	parse_qspi_ver_info

	if (( "${sys_rel}" > "${qspi_rel}" )); then
		# sys_rel > qspi_rel
		# need to update QSPI
		return 0
	elif (( "${sys_rel}" == "${qspi_rel}" )); then
		if (( "${sys_maj_ver}" > "${qspi_maj_ver}" )); then
			# sys_rel == qspi_rel
			# sys_maj_ver > qspi_maj_ver
			# need to update QSPI
			return 0
		elif (( "${sys_maj_ver}" == "${qspi_maj_ver}" )); then
			if (( "${sys_min_ver}" > "${qspi_min_ver}" )); then
				# sys_rel == qspi_rel
				# sys_maj_ver == qspi_maj_ver
				# sys_min_ver > qspi_min_ver
				# need to update QSPI
				return 0
			else
				return 1
			fi
		else
			return 1
		fi
	else
		return 1
	fi
}

auto_update_qspi () {
	# read system version
	read_sys_ver

	# read qspi version
	if [[ ("${tnspec}" == *"jetson-nano-qspi-sd"* ||
		"${tnspec}" == *"jetson-nano-2gb-devkit"*) &&
		-x "${T210REF_UPDATER}" ]]; then
		read_t210ref_qspi_ver_info
	elif [[ ("${tnspec}" == *"jetson-xavier-nx-devkit"*) &&
		-x "${T186REF_UPDATER}" ]]; then
		read_t186ref_qspi_ver_info
	else
		exit 0
	fi

	if update_qspi_check; then
		dpkg-reconfigure "${PACKAGE_NAME}"
	fi
}

if [ ! -r "${BOOT_CTRL_CONF}" ]; then
	echo "Error. Cannot open ${BOOT_CTRL_CONF} for reading."
	echo "Cannot install package. Exiting..."
	exit 1
fi

chipid=$( awk '/TEGRA_CHIPID/ {print $2}' "${BOOT_CTRL_CONF}" )
tnspec=$( awk '/TNSPEC/ {print $2}' "${BOOT_CTRL_CONF}" )

update_boot_ctrl_conf

case "${chipid}" in
	0x21 | 0x19)
		auto_update_qspi
		;;
esac
