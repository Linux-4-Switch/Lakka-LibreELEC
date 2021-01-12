# Copyright (c) 2017, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

include ../Makefile.l4tsdkdefs
TARGETS += $(NV_WINSYS)/ctree

CTREE_OBJS :=
CTREE_OBJS += $(NV_WINSYS)/main.o
CTREE_OBJS += $(NV_WINSYS)/array.o
CTREE_OBJS += $(NV_WINSYS)/branches.o
CTREE_OBJS += $(NV_WINSYS)/buildtree.o
CTREE_OBJS += $(NV_WINSYS)/firefly.o
CTREE_OBJS += $(NV_WINSYS)/ground.o
CTREE_OBJS += $(NV_WINSYS)/leaves.o
CTREE_OBJS += $(NV_WINSYS)/picture.o
CTREE_OBJS += $(NV_WINSYS)/random.o
CTREE_OBJS += $(NV_WINSYS)/screen.o
CTREE_OBJS += $(NV_WINSYS)/shaders.o
CTREE_OBJS += $(NV_WINSYS)/sky.o
CTREE_OBJS += $(NV_WINSYS)/slider.o
CTREE_OBJS += $(NV_WINSYS)/tree.o
CTREE_OBJS += $(NV_WINSYS)/vbo.o
CTREE_OBJS += $(NV_WINSYS)/vector.o
INTERMEDIATES += $(CTREE_OBJS)

CTREE_SHADER_STRS :=
CTREE_SHADER_STRS += lighting_vert.glslvh
CTREE_SHADER_STRS += simplecol_vert.glslvh
CTREE_SHADER_STRS += simpletex_vert.glslvh
CTREE_SHADER_STRS += overlaycol_vert.glslvh
CTREE_SHADER_STRS += overlaytex_vert.glslvh
CTREE_SHADER_STRS += solids_frag.glslfh
CTREE_SHADER_STRS += leaves_frag.glslfh
CTREE_SHADER_STRS += simplecol_frag.glslfh
CTREE_SHADER_STRS += simpletex_frag.glslfh
CTREE_SHADER_STRS += overlaycol_frag.glslfh
CTREE_SHADER_STRS += overlaytex_frag.glslfh
INTERMEDIATES += $(CTREE_SHADER_STRS)

CTREE_SHADER_BINS :=
CTREE_SHADER_BINS += lighting_vert.cgbin
CTREE_SHADER_BINS += simplecol_vert.cgbin
CTREE_SHADER_BINS += simpletex_vert.cgbin
CTREE_SHADER_BINS += overlaycol_vert.cgbin
CTREE_SHADER_BINS += overlaytex_vert.cgbin
CTREE_SHADER_BINS += solids_frag.cgbin
CTREE_SHADER_BINS += leaves_frag.cgbin
CTREE_SHADER_BINS += simplecol_frag.cgbin
CTREE_SHADER_BINS += simpletex_frag.cgbin
CTREE_SHADER_BINS += overlaycol_frag.cgbin
CTREE_SHADER_BINS += overlaytex_frag.cgbin
INTERMEDIATES += $(CTREE_SHADER_BINS)
ifeq ($(NV_USE_EXTERN_SHADERS),1)
ifeq ($(NV_USE_BINARY_SHADERS),1)
TARGETS += $(CTREE_SHADER_BINS)
endif
endif

CTREE_SHADER_HEXS :=
CTREE_SHADER_HEXS += lighting_vert.cghex
CTREE_SHADER_HEXS += simplecol_vert.cghex
CTREE_SHADER_HEXS += simpletex_vert.cghex
CTREE_SHADER_HEXS += overlaycol_vert.cghex
CTREE_SHADER_HEXS += overlaytex_vert.cghex
CTREE_SHADER_HEXS += solids_frag.cghex
CTREE_SHADER_HEXS += leaves_frag.cghex
CTREE_SHADER_HEXS += simplecol_frag.cghex
CTREE_SHADER_HEXS += simpletex_frag.cghex
CTREE_SHADER_HEXS += overlaycol_frag.cghex
CTREE_SHADER_HEXS += overlaytex_frag.cghex
INTERMEDIATES += $(CTREE_SHADER_HEXS)

CTREE_DEMOLIBS :=
CTREE_DEMOLIBS += ../nvtexfont/$(NV_WINSYS)/libnvtexfont2.a
CTREE_DEMOLIBS += ../nvgldemo/$(NV_WINSYS)/libnvgldemo.a

CTREE_LDLIBS :=
CTREE_LDLIBS += -lm
CTREE_LDLIBS += -lrt
CTREE_LDLIBS += -lpthread
CTREE_LDLIBS += -lEGL
CTREE_LDLIBS += -l:libGLESv2.so.2
CTREE_LDLIBS += ${NV_PLATFORM_WINSYS_LIBS}

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

$(NV_WINSYS)/ctree: $(CTREE_OBJS) $(CTREE_DEMOLIBS)
	$(LD) $(LDFLAGS) -o $@ $^ $(CTREE_LDLIBS)

ifeq ($(NV_USE_EXTERN_SHADERS),0)
ifeq ($(NV_USE_BINARY_SHADERS),1)
$(CTREE_OBJS) : $(CTREE_SHADER_HEXS)
else
$(CTREE_OBJS) : $(CTREE_SHADER_STRS)
endif
endif

define demolib-rule
$(1): FORCE
	$(MAKE) -C $$(subst $$(NV_WINSYS)/,,$$(dir $$@))
endef
$(foreach demolib,$(CTREE_DEMOLIBS),$(eval $(call demolib-rule,$(demolib))))

