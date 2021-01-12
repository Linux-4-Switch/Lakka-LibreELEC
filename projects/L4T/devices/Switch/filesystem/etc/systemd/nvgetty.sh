#!/bin/bash
#
# Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
#
if [ -e "/proc/device-tree/compatible" ]; then
	CHIP="$(tr -d '\0' < /proc/device-tree/compatible)"
	if [[ "${CHIP}" =~ "tegra194" ]]; then
		setsid /sbin/getty -L 115200 ttyTHS0
	elif [[ "${CHIP}" =~ "tegra210" ]]; then
		setsid /sbin/getty -L 115200 ttyTHS1
	fi
fi
