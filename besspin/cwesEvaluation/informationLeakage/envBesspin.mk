## Parse the name containg the main invocation to figure out which variants
## to use for the test script, store, interpreter. With exception of nonstandard tests

GENERIC_SRC = $(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c)
ifeq ($(VARIANT_NAMES),)
	VARIANT_SRC	:= 
	GENERIC_SRC += $(wildcard $(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstd_utils/*.c)
else
	VARIANT_SRC	= $(addprefix $(INC_BESSPIN_TOOL_SUITE)/,$(VARIANT_NAMES))
	GENERIC_SRC += $(wildcard $(INC_BESSPIN_TOOL_SUITE)/informationLeakage/control/*.c)   \
	              $(wildcard $(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/*.c)
endif

$(info VARIANT_NAMES=$(VARIANT_NAMES))
$(info VARIANT_SRC=$(VARIANT_SRC))
$(info GENERIC_SRC=$(GENERIC_SRC))

CFLAGS += -DBESSPIN_TOOL_SUITE -DBESSPIN_FREERTOS
WERROR = 

ifeq ($(BSP),qemu)
	CFLAGS += -DBESSPIN_QEMU
	APP_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

	APP_INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/include
	APP_INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/include/parameters
	APP_INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)

	VPATH += \
		$(APP_SRC_DIR) \
		$(APP_SRC_DIR)/full_demo \
		$(INC_BESSPIN_TOOL_SUITE) \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/control \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/stores \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/interpreters \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests \
		$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstd_utils
else
	CFLAGS += -DBESSPIN_FPGA
	DEMO_SRC = main.c $(VARIANT_SRC) $(GENERIC_SRC)

	INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/include
	INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/include/parameters
	INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)
endif

# Enable capability leakage tests
ifeq ($(CHERI),1)
TARGET_CFLAGS+=	-D__IEX_GEN__CAPABILITIES__
endif

$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/stores/fragmented.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/stores/cached.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/stores/flatstore.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/stores/separate.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/control/control.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/classifydeclassify.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/indexing.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/systemconfig.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/directsys.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/indexing2.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/setenv.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/atoi.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/error.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/loginmsg.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/cache.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/tests/markprivate.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/interpreters/simpleatoi.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/interpreters/binterpreter.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/fdispatch.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/sysconfig.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/search.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/mark_private.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/functions.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/errorf.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/broadcast.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/count.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/declassify.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/classify.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/login.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/set_env.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/functions/direct.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstd_utils/noClearRealloc.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstd_utils/nonstdCommon.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstandard/test_noClearMalloc.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstandard/test_noClearReallocExpand.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
$(INC_BESSPIN_TOOL_SUITE)/informationLeakage/nonstandard/test_noClearReallocShrink.o: _TARGET_CFLAGS=$(TARGET_CFLAGS)
