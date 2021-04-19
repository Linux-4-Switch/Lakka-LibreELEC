################################################################################
#      This file is part of LibreELEC - http://www.libreelec.tv
#      Copyright (C) 2016 Team LibreELEC
#
#  LibreELEC is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  LibreELEC is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with LibreELEC.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

PKG_NAME="glslang"
PKG_VERSION="e6a0e7f"
PKG_ARCH="any"
PKG_LICENSE="Apache 2.0"
PKG_SITE="https://github.com/KhronosGroup/glslang"
PKG_URL="https://github.com/KhronosGroup/glslang/archive/refs/tags/master-tot.tar.gz"
PKG_DEPENDS_TARGET="toolchain cmake:host Python3"
PKG_TOOLCHAIN="cmake-make"
PKG_SECTION="graphics"
PKG_SHORTDESC="An OpenGL and OpenGL ES shader front end and validator."

PKG_IS_ADDON="no"
PKG_AUTORECONF="no"

PKG_CMAKE_OPTS_TARGET=""

pre_configure_target() {
  CURDIR=$(pwd)
  cd $PKG_BUILD/External
  git clone https://github.com/KhronosGroup/Vulkan-Headers.git
  cd Vulkan-Headers
  git checkout tags/v1.2.174
  cd ..
  git clone https://github.com/google/googletest.git
  cd googletest
  git checkout 0c400f67fcf305869c5fb113dd296eca266c9725
  cd $PKG_BUILD
  ./update_glslang_sources.py
  cd $CURDIR
}
