#
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

NV_WINSYS := wayland
include ../Makefile.l4tsdkdefs
TARGETS += $(NV_WINSYS)/weston-dmabuf-formats

WESTON-DMABUF-FORMATS_OBJS :=
WESTON-DMABUF-FORMATS_OBJS += $(NV_WINSYS)/weston-dmabuf-formats.o
INTERMEDIATES += $(WESTON-DMABUF-FORMATS_OBJS)

EGLSTREAMCUBE_DEMOLIBS :=
EGLSTREAMCUBE_DEMOLIBS += ../nvgldemo/$(NV_WINSYS)/libnvgldemo.a

WESTON-DMABUF-FORMATS_LDLIBS :=
WESTON-DMABUF-FORMATS_LDLIBS += -lm
WESTON-DMABUF-FORMATS_LDLIBS += -lrt
WESTON-DMABUF-FORMATS_LDLIBS += -lpthread
WESTON-DMABUF-FORMATS_LDLIBS += -lEGL
WESTON-DMABUF-FORMATS_LDLIBS += -l:libGLESv2.so.2
WESTON-DMABUF-FORMATS_LDLIBS += -l:libnvbuf_utils.so
WESTON-DMABUF-FORMATS_LDLIBS += -l:libweston-6.so.0
WESTON-DMABUF-FORMATS_LDLIBS += -l:libweston-desktop-6.so.0
WESTON-DMABUF-FORMATS_LDLIBS += -l:fullscreen-shell.so
WESTON-DMABUF-FORMATS_LDLIBS += -l:libdrm.so.2
WESTON-DMABUF-FORMATS_LDLIBS += -l:libnvgbm.so
WESTON-DMABUF-FORMATS_LDLIBS += ${NV_PLATFORM_WINSYS_LIBS}

ifeq ($(findstring $(NV_WINSYS),egldevice screen wayland x11),)
all:
	echo Sample not supported for NV_WINSYS=
else
all: $(TARGETS)
endif

clean:
	rm -rf $(TARGETS) $(INTERMEDIATES)

.PHONY: FORCE
FORCE:

$(NV_WINSYS)/weston-dmabuf-formats: $(WESTON-DMABUF-FORMATS_OBJS) $(WESTON-DMABUF-FORMATS_DEMOLIBS)
	$(LD) $(LDFLAGS) -o $@ $^ $(WESTON-DMABUF-FORMATS_LDLIBS)

define demolib-rule
$(1): FORCE
	$(MAKE) -C $$(subst $$(NV_WINSYS)/,,$$(dir $$@))
endef
$(foreach demolib,$(WESTON-DMABUF-FORMATS_DEMOLIBS),$(eval $(call demolib-rule,$(demolib))))
