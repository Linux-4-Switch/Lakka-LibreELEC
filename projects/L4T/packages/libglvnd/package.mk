# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

PKG_NAME="libglvnd"
PKG_VERSION="1.3.2"
PKG_LICENSE="GPL"
PKG_SITE="https://github.com/NVIDIA/libglvnd"
PKG_URL="https://gitlab.freedesktop.org/glvnd/libglvnd/-/archive/v${PKG_VERSION}/libglvnd-v${PKG_VERSION}.tar"
PKG_DEPENDS_TARGET="toolchain libX11 libXext xorgproto"
PKG_LONGDESC="libglvnd is a vendor-neutral dispatch layer for arbitrating OpenGL API calls between multiple vendors."
PKG_TOOLCHAIN="autotools"

if [ ! "${PLATFORM}" == "L4T" ]; then
  if [ "$OPENGLES_SUPPORT" = "no" ]; then
    PKG_CONFIGURE_OPTS_TARGET+=" --disable-gles"
  fi
else
  PKG_CONFIGURE_OPTS_TARGET+=" --enable-headers --enable-egl --enable-glx --enable-gles1 --enable-gles2"
fi

#post_makeinstall_target() {
#  if [ "${DISPLAYSERVER}" = "x11" ]; then
    # Remove old symlinks to GLVND libGL.so.1.7.0
    #safe_remove              ${INSTALL}/usr/lib/libGL.so
    #safe_remove              ${INSTALL}/usr/lib/libGL.so.1
    # Create new symlinks to /var/lib/libGL.so
#    ln -sf libGL.so.1        ${INSTALL}/usr/lib/libGL.so
    #ln -sf /var/lib/libGL.so ${INSTALL}/usr/lib/libGL.so.1
    # Create new symlink to GLVND libGL.so.1.7.0
#    ln -sf libGL.so.1.7.0    ${INSTALL}/usr/lib/libGL_glvnd.so.1
#  fi
#}
