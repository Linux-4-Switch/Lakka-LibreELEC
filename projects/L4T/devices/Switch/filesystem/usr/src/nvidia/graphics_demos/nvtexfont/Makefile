# Copyright (c) 2017, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

include ../Makefile.l4tsdkdefs
TARGETS += $(NV_WINSYS)/libnvtexfont2.a

NVTEXFONT2_OBJS :=
NVTEXFONT2_OBJS += $(NV_WINSYS)/nvtexfont2.o
NVTEXFONT2_OBJS += $(NV_WINSYS)/nvtexfont2-rast.o
NVTEXFONT2_OBJS += $(NV_WINSYS)/nvtexfont2-vect.o
INTERMEDIATES += $(NVTEXFONT2_OBJS)

NVTEXFONT2_SHADER_STRS :=
NVTEXFONT2_SHADER_STRS += vtxraster.glslvh
NVTEXFONT2_SHADER_STRS += vtxvector.glslvh
NVTEXFONT2_SHADER_STRS += colraster.glslfh
NVTEXFONT2_SHADER_STRS += colvector.glslfh
INTERMEDIATES += $(NVTEXFONT2_SHADER_STRS)

NVTEXFONT2_SHADER_BINS :=
NVTEXFONT2_SHADER_BINS += vtxraster.cgbin
NVTEXFONT2_SHADER_BINS += vtxvector.cgbin
NVTEXFONT2_SHADER_BINS += colraster.cgbin
NVTEXFONT2_SHADER_BINS += colvector.cgbin
INTERMEDIATES += $(NVTEXFONT2_SHADER_BINS)
ifeq ($(NV_USE_EXTERN_SHADERS),1)
ifeq ($(NV_USE_BINARY_SHADERS),1)
TARGETS += $(NVTEXFONT2_SHADER_BINS)
endif
endif

NVTEXFONT2_SHADER_HEXS :=
NVTEXFONT2_SHADER_HEXS += vtxraster.cghex
NVTEXFONT2_SHADER_HEXS += vtxvector.cghex
NVTEXFONT2_SHADER_HEXS += colraster.cghex
NVTEXFONT2_SHADER_HEXS += colvector.cghex
INTERMEDIATES += $(NVTEXFONT2_SHADER_HEXS)

NVTEXFONT2_DEMOLIBS :=

NVTEXFONT2_LDLIBS :=

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

$(NV_WINSYS)/libnvtexfont2.a: $(NV_WINSYS)/libnvtexfont2.a($(NVTEXFONT2_OBJS))

ifeq ($(NV_USE_EXTERN_SHADERS),0)
ifeq ($(NV_USE_BINARY_SHADERS),1)
$(NVTEXFONT2_OBJS) : $(NVTEXFONT2_SHADER_HEXS)
else
$(NVTEXFONT2_OBJS) : $(NVTEXFONT2_SHADER_STRS)
endif
endif

define demolib-rule
$(1): FORCE
	$(MAKE) -C $$(subst $$(NV_WINSYS)/,,$$(dir $$@))
endef
$(foreach demolib,$(NVTEXFONT2_DEMOLIBS),$(eval $(call demolib-rule,$(demolib))))

