
include ../kaldi.mk

ifeq ($(PYIDLAK), true)

PY_SUBDIRS = txp vocoder

all: $(PY_SUBDIRS)
	@echo "Finished making python wrappers"

.PHONY: clean_py
clean_py:
	-rm -rf *.pyc __pycache__ test/*.pyc test/__pycache__
	
clean:  clean_py
	-for x in $(PY_SUBDIRS); do $(MAKE) -C $$x clean; done

.PHONY: $(PY_SUBDIRS)
$(PY_SUBDIRS):
	$(MAKE) -C $@

endif # PYIDLAK
