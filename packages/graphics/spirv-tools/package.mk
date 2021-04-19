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

PKG_NAME="spirv-tools"
PKG_VERSION="a02a920"
PKG_ARCH="any"
PKG_LICENSE="Apache 2.0"
PKG_SITE="https://github.com/KhronosGroup/SPIRV-Tools"
PKG_URL="https://github.com/KhronosGroup/SPIRV-Tools/archive/refs/tags/v2019.3.tar.gz"
PKG_DEPENDS_TARGET="toolchain cmake:host Python3 vulkan-validationlayers"
PKG_SECTION="graphics"
PKG_SHORTDESC="The SPIR-V Tools project provides an API and commands for processing SPIR-V modules."
PKG_TOOLCHAIN="cmake-make"
PKG_IS_ADDON="no"
PKG_AUTORECONF="no"

PKG_CMAKE_OPTS_TARGET="-DSPIRV_WERROR=OFF" #\
                       #-DSPIRV-Headers_SOURCE_DIR=$PKG_BUILD/external/spirv-headers"

pre_configure_target() {
  CURPWD=$(pwd)
  cd $PKG_BUILD/external
  git clone https://github.com/KhronosGroup/SPIRV-Headers.git spirv-headers
  cd spirv-headers
  git checkout af64a9e826bf5bb5fcd2434dd71be1e41e922563
  cd ..
  #git clone https://github.com/google/googletest.git          googletest
  #git clone https://github.com/google/effcee.git              effcee
  #git clone https://github.com/google/re2.git                 re2
  cd $CURPWD
}
