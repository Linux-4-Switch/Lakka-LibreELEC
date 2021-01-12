# Copyright (c) 2017, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

include ../Makefile.l4tsdkdefs
TARGETS += $(NV_WINSYS)/gears

GEARS_OBJS :=
GEARS_OBJS += $(NV_WINSYS)/gears.o
INTERMEDIATES += $(GEARS_OBJS)

GEARS_DEMOLIBS :=
GEARS_DEMOLIBS += ../gears-lib/$(NV_WINSYS)/libgears.a
GEARS_DEMOLIBS += ../nvgldemo/$(NV_WINSYS)/libnvgldemo.a

GEARS_LDLIBS :=
GEARS_LDLIBS += -lm
GEARS_LDLIBS += -lrt
GEARS_LDLIBS += -lpthread
GEARS_LDLIBS += -lEGL
GEARS_LDLIBS += -l:libGLESv2.so.2
GEARS_LDLIBS += ${NV_PLATFORM_WINSYS_LIBS}

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

$(NV_WINSYS)/gears: $(GEARS_OBJS) $(GEARS_DEMOLIBS)
	$(LD) $(LDFLAGS) -o $@ $^ $(GEARS_LDLIBS)

define demolib-rule
$(1): FORCE
	$(MAKE) -C $$(subst $$(NV_WINSYS)/,,$$(dir $$@))
endef
$(foreach demolib,$(GEARS_DEMOLIBS),$(eval $(call demolib-rule,$(demolib))))

