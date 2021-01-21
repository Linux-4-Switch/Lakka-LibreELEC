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

PKG_NAME="tegra-bsp"
PKG_VERSION="32.4.4"
PKG_ARCH="any"
PKG_DEPENDS_HOST=""
PKG_DEPENDS_TARGET="toolchain" 
PKG_SITE="https://developer.nvidia.com/EMBEDDED/linux-tegra%20/"
case "$DEVICE" in
  tx2|xavier|agx)
    PKG_URL="https://developer.nvidia.com/embedded/L4T/r32_Release_v4.4/r32_Release_v4.4-GMC3/T186/Tegra186_Linux_R32.4.4_aarch64.tbz2"
    BSP=Tegra186_Linux_R32.4.4_aarch64.tbz2
    ;;
  tx1|nano|Switch)
    PKG_URL="https://developer.nvidia.com/embedded/L4T/r32_Release_v4.4/r32_Release_v4.4-GMC3/T210/Tegra210_Linux_R32.4.4_aarch64.tbz2"
    BSP=Tegra210_Linux_R32.4.4_aarch64.tbz2
    ;;
esac
PKG_TOOLCHAIN="make"
PKG_AUTORECONF="no"

makeinstall_target() {
  tar xf $BSP Linux_for_Tegra/nv_tegra
  for tbz in `ls Linux_for_Tegra/nv_tegra/*.tbz2`; do tar xf $tbz; done
  tar xf Linux_for_Tegra/nv_tegra/nv_sample_apps/nvgstapps.tbz2
  mv lib/* usr/lib/
  mv usr/sbin/* usr/bin/
  mv usr/lib/aarch64-linux-gnu/* usr/lib/
}

make_target() {
  :
}
