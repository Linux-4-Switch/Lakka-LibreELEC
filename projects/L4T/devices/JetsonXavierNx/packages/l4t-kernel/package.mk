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

PKG_NAME="l4t-kernel"
PKG_VERSION="30db1218aa60785cf3cef8a0a49f3c23179eee48"
PKG_GIT_CLONE_BRANCH="linux-rel32"
PKG_ARCH="any"
PKG_LICENSE="nonfree"
PKG_SITE="https://gitlab.com/switchroot/kernel/l4t-kernel-4.9.git"
PKG_URL="$PKG_SITE"
PKG_CLEAN="linux"
PKG_TOOLCHAIN="manual"

make_target() {
	:
}

makeinstall_target() {
	:
}

make_host() {
	:
}

makeinstall_host() {
    make -C ARCH=arm64 headers
  mkdir -p $SYSROOT_PREFIX/usr/include
    make -C ARCH=arm64 INSTALL_HDR_PATH=$SYSROOT_PREFIX/usr/include headers_install

}

make_init() {
	:
}

makeinstall_init() {
	:
}
