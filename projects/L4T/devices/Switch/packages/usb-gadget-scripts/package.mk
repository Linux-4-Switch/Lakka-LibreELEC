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

PKG_NAME="usb-gadget-scripts"
PKG_VERSION="1"
PKG_ARCH="any"
PKG_DEPENDS_HOST=""
PKG_DEPENDS_TARGET="toolchain" 
PKG_TOOLCHAIN="make"

makeinstall_target() {
  mkdir -p $PKG_BUILD/install
  mkdir -p $INSTALL

  cd $PKG_BUILD/install
  mkdir -p usr/bin
  mkdir -p usr/lib/systemd/system/multi-user.target.wants
  cp $PKG_DIR/assets/usb-gadget.sh usr/bin/
  chmod +x usr/bin/usb-gadget.sh
  cp $PKG_DIR/assets/usb-gadget.service usr/lib/systemd/system/
  cp $PKG_DIR/assets/usb-tty.service usr/lib/systemd/system/
  cd usr/lib/systemd/system/
  chmod +x *.service
  ln -s usb-gadget.service multi-user.target.wants/usb-gadget.service
  ln -s usb-tty.service multi-user.target.wants/usb-tty.service
  cd ../../../../../
  
  cp -PRv install/* $INSTALL/ 
    
}

make_target() {
  :
}
