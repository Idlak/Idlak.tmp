
include ../kaldi.mk

ifeq ($(PYIDLAK), true)

PY_SUBDIRS = txp

all: $(PY_SUBDIRS)
	@echo "Finished making python wrappers"

clean:
	-for x in $(PY_SUBDIRS); do $(MAKE) -C $$x clean; done

.PHONY: $(PY_SUBDIRS)
$(PY_SUBDIRS):
	$(MAKE) -C $@

endif # PYIDLAK