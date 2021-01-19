# Copyright (c) 2017, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

include ../Makefile.l4tsdkdefs
TARGETS += $(NV_WINSYS)/eglstreamcube

EGLSTREAMCUBE_OBJS :=
EGLSTREAMCUBE_OBJS += $(NV_WINSYS)/eglstreamcube.o
INTERMEDIATES += $(EGLSTREAMCUBE_OBJS)

EGLSTREAMCUBE_SHADER_STRS :=
EGLSTREAMCUBE_SHADER_STRS += cube_vert.glslvh
EGLSTREAMCUBE_SHADER_STRS += cube_frag.glslfh
EGLSTREAMCUBE_SHADER_STRS += logo_frag.glslfh
INTERMEDIATES += $(EGLSTREAMCUBE_SHADER_STRS)

EGLSTREAMCUBE_SHADER_BINS :=
EGLSTREAMCUBE_SHADER_BINS += cube_vert.cgbin
EGLSTREAMCUBE_SHADER_BINS += cube_frag.cgbin
EGLSTREAMCUBE_SHADER_BINS += logo_frag.cgbin
INTERMEDIATES += $(EGLSTREAMCUBE_SHADER_BINS)
ifeq ($(NV_USE_EXTERN_SHADERS),1)
ifeq ($(NV_USE_BINARY_SHADERS),1)
TARGETS += $(EGLSTREAMCUBE_SHADER_BINS)
endif
endif

EGLSTREAMCUBE_SHADER_HEXS :=
EGLSTREAMCUBE_SHADER_HEXS += cube_vert.cghex
EGLSTREAMCUBE_SHADER_HEXS += cube_frag.cghex
EGLSTREAMCUBE_SHADER_HEXS += logo_frag.cghex
INTERMEDIATES += $(EGLSTREAMCUBE_SHADER_HEXS)

EGLSTREAMCUBE_DEMOLIBS :=
EGLSTREAMCUBE_DEMOLIBS += ../nvgldemo/$(NV_WINSYS)/libnvgldemo.a

EGLSTREAMCUBE_LDLIBS :=
EGLSTREAMCUBE_LDLIBS += -lm
EGLSTREAMCUBE_LDLIBS += -lrt
EGLSTREAMCUBE_LDLIBS += -lpthread
EGLSTREAMCUBE_LDLIBS += -lEGL
EGLSTREAMCUBE_LDLIBS += -l:libGLESv2.so.2
EGLSTREAMCUBE_LDLIBS += ${NV_PLATFORM_WINSYS_LIBS}

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

$(NV_WINSYS)/eglstreamcube: $(EGLSTREAMCUBE_OBJS) $(EGLSTREAMCUBE_DEMOLIBS)
	$(LD) $(LDFLAGS) -o $@ $^ $(EGLSTREAMCUBE_LDLIBS)

ifeq ($(NV_USE_EXTERN_SHADERS),0)
ifeq ($(NV_USE_BINARY_SHADERS),1)
$(EGLSTREAMCUBE_OBJS) : $(EGLSTREAMCUBE_SHADER_HEXS)
else
$(EGLSTREAMCUBE_OBJS) : $(EGLSTREAMCUBE_SHADER_STRS)
endif
endif

define demolib-rule
$(1): FORCE
	$(MAKE) -C $$(subst $$(NV_WINSYS)/,,$$(dir $$@))
endef
$(foreach demolib,$(EGLSTREAMCUBE_DEMOLIBS),$(eval $(call demolib-rule,$(demolib))))

