################################################################################
#      This file is part of OpenELEC - http://www.openelec.tv
#      Copyright (C) 2009-2012 Stephan Raue (stephan@openelec.tv)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with OpenELEC.tv; see the file COPYING.  If not, write to
#  the Free Software Foundation, 51 Franklin Street, Suite 500, Boston, MA 02110, USA.
#  http://www.gnu.org/copyleft/gpl.html
################################################################################

PKG_NAME="linux"
PKG_LICENSE="GPL"
PKG_SITE="http://www.kernel.org"
PKG_DEPENDS_HOST="ccache:host openssl:host gcc-linaro-aarch64-linux-gnu:host"
PKG_DEPENDS_TARGET="toolchain linux:host kmod:host xz:host wireless-regdb keyutils kernel-firmware openssl:host gcc-linaro-aarch64-linux-gnu:host"
PKG_DEPENDS_INIT="toolchain"
PKG_VERSION="4.9.140"
PKG_ARCH="aarch64"
PKG_TOOLCHAIN="make"
PKG_VERSION="linux-rel32-rebase"
PKG_URL="https://gitlab.com/Azkali/l4t-kernel-4.9/-/archive/$PKG_VERSION/l4t-kernel-4.9-$PKG_VERSION.tar.gz"

PKG_IS_ADDON="no"
PKG_AUTORECONF="no"
TARGET_ARCH="arm64"

export PATH=$TOOLCHAIN/lib/gcc-linaro-aarch64-linux-gnu/bin/:$PATH
TARGET_PREFIX=aarch64-linux-gnu-
OLD_CROSS_COMPILE=$CROSS_COMPILE
export CROSS_COMPILE=$TARGET_PREFIX # necessary for Linux 5
export C_INCLUDE_PATH="$TOOLCHAIN/include:$C_INCLUDE_PATH"
export LIBRARY_PATH="$TOOLCHAIN/lib:$LIBRARY_PATH"

makeinstall_host() {
	make ARCH=$TARGET_ARCH INSTALL_HDR_PATH=dest headers_install
}

pre_make_target() {
	(	
		cd $ROOT
		rm -rf $BUILD/initramfs
		$SCRIPTS/install initramfs
	)
	pkg_lock_status "ACTIVE" "linux:target" "build"

	mkdir -p $PKG_BUILD/external-firmware
	cp -a $(get_build_dir kernel-firmware)/{nvidia,brcm} $PKG_BUILD/external-firmware

	FW_LIST="$(find $PKG_BUILD/external-firmware \( -type f -o -type l \) \( -iname '*.bin' -o -iname '*.txt' -o -iname '*.hcd' \) | sed 's|.*external-firmware/||' | sort | xargs)"
	sed -i "s|CONFIG_EXTRA_FIRMWARE=.*|CONFIG_EXTRA_FIRMWARE=\"${FW_LIST}\"|" $PKG_BUILD/.config
}

make_target() {
	cp arch/arm64/configs/tegra_linux_defconfig .config

	make olddefconfig
	make prepare
	make modules_prepare


	WERROR=0 \
	NO_LIBPERL=1 \
	NO_LIBPYTHON=1 \
	NO_SLANG=1 \
	NO_GTK2=1 \
	NO_LIBNUMA=1 \
	NO_LIBAUDIT=1 \
	NO_LZMA=1 \
	NO_SDT=1 \
	CROSS_COMPILE="$TARGET_PREFIX" \
	JOBS="$CONCURRENCY_MAKE_LEVEL" \
	make
}

makeinstall_target() {
	make INSTALL_MOD_PATH=$INSTALL/$(get_kernel_overlay_dir) modules_install
	rm -f $INSTALL/$(get_kernel_overlay_dir)/lib/modules/*/build
	rm -f $INSTALL/$(get_kernel_overlay_dir)/lib/modules/*/source

	cp -p arch/$TARGET_KERNEL_ARCH/boot/dts/*.dtb $INSTALL/usr/share/bootloader
}

post_install() {
	mkdir -p $INSTALL/$(get_full_firmware_dir)/

	# regdb and signature is now loaded as firmware by 4.15+
	if grep -q ^CONFIG_CFG80211_REQUIRE_SIGNED_REGDB= $PKG_BUILD/.config; then
		cp $(get_build_dir wireless-regdb)/regulatory.db{,.p7s} $INSTALL/$(get_full_firmware_dir)
	fi

	# bluez looks in /etc/firmware/
	ln -sf /usr/lib/firmware/ $INSTALL/etc/firmware

	export CROSS_COMPILE=$OLD_CROSS_COMPILE
}
