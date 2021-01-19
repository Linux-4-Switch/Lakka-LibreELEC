# Copyright (c) 2017, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

include ../Makefile.l4tsdkdefs
TARGETS += $(NV_WINSYS)/libgears.a

GEARSLIB_OBJS :=
GEARSLIB_OBJS += $(NV_WINSYS)/gearslib.o
INTERMEDIATES += $(GEARSLIB_OBJS)

GEARSLIB_SHADER_STRS :=
GEARSLIB_SHADER_STRS += gears_vert.glslvh
GEARSLIB_SHADER_STRS += gears_frag.glslfh
INTERMEDIATES += $(GEARSLIB_SHADER_STRS)

GEARSLIB_SHADER_BINS :=
GEARSLIB_SHADER_BINS += gears_vert.cgbin
GEARSLIB_SHADER_BINS += gears_frag.cgbin
INTERMEDIATES += $(GEARSLIB_SHADER_BINS)
ifeq ($(NV_USE_EXTERN_SHADERS),1)
ifeq ($(NV_USE_BINARY_SHADERS),1)
TARGETS += $(GEARSLIB_SHADER_BINS)
endif
endif

GEARSLIB_SHADER_HEXS :=
GEARSLIB_SHADER_HEXS += gears_vert.cghex
GEARSLIB_SHADER_HEXS += gears_frag.cghex
INTERMEDIATES += $(GEARSLIB_SHADER_HEXS)

GEARSLIB_DEMOLIBS :=

GEARSLIB_LDLIBS :=

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

$(NV_WINSYS)/libgears.a: $(NV_WINSYS)/libgears.a($(GEARSLIB_OBJS))

ifeq ($(NV_USE_EXTERN_SHADERS),0)
ifeq ($(NV_USE_BINARY_SHADERS),1)
$(GEARSLIB_OBJS) : $(GEARSLIB_SHADER_HEXS)
else
$(GEARSLIB_OBJS) : $(GEARSLIB_SHADER_STRS)
endif
endif

define demolib-rule
$(1): FORCE
	$(MAKE) -C $$(subst $$(NV_WINSYS)/,,$$(dir $$@))
endef
$(foreach demolib,$(GEARSLIB_DEMOLIBS),$(eval $(call demolib-rule,$(demolib))))

