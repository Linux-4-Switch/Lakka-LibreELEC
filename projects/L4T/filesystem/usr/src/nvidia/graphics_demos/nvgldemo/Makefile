# Copyright (c) 2017, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

include ../Makefile.l4tsdkdefs
TARGETS += $(NV_WINSYS)/libnvgldemo.a

NVGLDEMO_OBJS :=
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_main.o
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_parse.o
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_shader.o
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_math.o
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_texture.o
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_socket.o
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_os_posix.o
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_preswap.o
NVGLDEMO_OBJS += $(NV_WINSYS)/nvgldemo_cqueue.o
ifeq ($(NV_WINSYS),egldevice)
 NVGLDEMO_OBJS += egldevice/nvgldemo_win_egldevice.o
 NV_PLATFORM_CPPFLAGS += -DNVGLDEMO_HAS_DEVICE
endif
ifeq ($(NV_WINSYS),screen)
 NVGLDEMO_OBJS += screen/nvgldemo_win_screen.o
endif
ifeq ($(NV_WINSYS),wayland)
 NVGLDEMO_OBJS += wayland/nvgldemo_win_wayland.o
endif
ifeq ($(NV_WINSYS),x11)
 NVGLDEMO_OBJS += x11/nvgldemo_win_x11.o
endif
INTERMEDIATES += $(NVGLDEMO_OBJS)

NVGLDEMO_DEMOLIBS :=

NVGLDEMO_LDLIBS :=

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

$(NV_WINSYS)/libnvgldemo.a: $(NV_WINSYS)/libnvgldemo.a($(NVGLDEMO_OBJS))

define demolib-rule
$(1): FORCE
	$(MAKE) -C $$(subst $$(NV_WINSYS)/,,$$(dir $$@))
endef
$(foreach demolib,$(NVGLDEMO_DEMOLIBS),$(eval $(call demolib-rule,$(demolib))))

