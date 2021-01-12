# Copyright (c) 2017, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

include ../Makefile.l4tsdkdefs
TARGETS += $(NV_WINSYS)/gearscube

GEARSCUBE_OBJS :=
GEARSCUBE_OBJS += $(NV_WINSYS)/gearscube.o
INTERMEDIATES += $(GEARSCUBE_OBJS)

GEARSCUBE_SHADER_STRS :=
GEARSCUBE_SHADER_STRS += cube_vert.glslvh
GEARSCUBE_SHADER_STRS += cube_frag.glslfh
INTERMEDIATES += $(GEARSCUBE_SHADER_STRS)

GEARSCUBE_SHADER_BINS :=
GEARSCUBE_SHADER_BINS += cube_vert.cgbin
GEARSCUBE_SHADER_BINS += cube_frag.cgbin
INTERMEDIATES += $(GEARSCUBE_SHADER_BINS)
ifeq ($(NV_USE_EXTERN_SHADERS),1)
ifeq ($(NV_USE_BINARY_SHADERS),1)
TARGETS += $(GEARSCUBE_SHADER_BINS)
endif
endif

GEARSCUBE_SHADER_HEXS :=
GEARSCUBE_SHADER_HEXS += cube_vert.cghex
GEARSCUBE_SHADER_HEXS += cube_frag.cghex
INTERMEDIATES += $(GEARSCUBE_SHADER_HEXS)

GEARSCUBE_DEMOLIBS :=
GEARSCUBE_DEMOLIBS += ../gears-lib/$(NV_WINSYS)/libgears.a
GEARSCUBE_DEMOLIBS += ../nvgldemo/$(NV_WINSYS)/libnvgldemo.a

GEARSCUBE_LDLIBS :=
GEARSCUBE_LDLIBS += -lm
GEARSCUBE_LDLIBS += -lrt
GEARSCUBE_LDLIBS += -lpthread
GEARSCUBE_LDLIBS += -lEGL
GEARSCUBE_LDLIBS += -l:libGLESv2.so.2
GEARSCUBE_LDLIBS += ${NV_PLATFORM_WINSYS_LIBS}

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

$(NV_WINSYS)/gearscube: $(GEARSCUBE_OBJS) $(GEARSCUBE_DEMOLIBS)
	$(LD) $(LDFLAGS) -o $@ $^ $(GEARSCUBE_LDLIBS)

ifeq ($(NV_USE_EXTERN_SHADERS),0)
ifeq ($(NV_USE_BINARY_SHADERS),1)
$(GEARSCUBE_OBJS) : $(GEARSCUBE_SHADER_HEXS)
else
$(GEARSCUBE_OBJS) : $(GEARSCUBE_SHADER_STRS)
endif
endif

define demolib-rule
$(1): FORCE
	$(MAKE) -C $$(subst $$(NV_WINSYS)/,,$$(dir $$@))
endef
$(foreach demolib,$(GEARSCUBE_DEMOLIBS),$(eval $(call demolib-rule,$(demolib))))

