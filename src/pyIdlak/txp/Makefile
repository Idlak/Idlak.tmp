
include ../../kaldi.mk

ifeq ($(PYIDLAK), true)

OBJFILES = python-txp-api.o pyIdlak_txp_wrap.o

LIBNAME = _pyIdlak_txp

ADDLIBS = ../../idlaktxp/idlak-txp.a ../../util/kaldi-util.a ../../matrix/kaldi-matrix.a ../../base/kaldi-base.a

EXTRA_CXXFLAGS = -fPIC -I$(PYTHONDEVINC) -I$(PCREROOT)/include -I$(EXPATROOT)/include -I$(PUJIXMLROOT)/src -I../..
EXTRA_LDLIBS = -Wl,-rpath,"$(PCREROOT)/lib" $(PCREROOT)/lib/libpcre.so $(EXPATROOT)/lib/libexpat.so

ifeq ($(PYTHONDEVLIBDIR),)
  PYLIBFLAG = -l$(PYTHONDEVLIB)
else
  PYLIBFLAG = -L$(PYTHONDEVLIBDIR) -l$(PYTHONDEVLIB)
endif
EXTRA_LDLIBS += $(PYLIBFLAG)

include ../../makefiles/default_rules.mk

ifeq ($(KALDI_FLAVOR), dynamic)
  STATICLIB =
else
  STATICLIB = _pyIdlak_txp.a
endif

.PHONY: wrapper
wrapper:
	$(SWIG) -c++ -python -o pyIdlak_txp_wrap.cc pyIdlak_txp.i
pyIdlak_txp_wrap.o: wrapper

sharedlib: $(STATICLIB)
ifeq ($(KALDI_FLAVOR), dynamic)
  ifeq ($(shell uname), Darwin)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_txp.dylib _pyIdlak_txp.dylib
  else ifeq ($(shell uname), Linux)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_txp.so _pyIdlak_txp.so
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
else
  ifeq ($(shell uname), Darwin)
	$(CXX) -dynamiclib -o _pyIdlak_txp.dylib -install_name @rpath/_pyIdlak_txp.a $(LDFLAGS) $(LDLIBS)
  else ifeq ($(shell uname), Linux)
	# Building shared library from static (static was compiled with -fPIC)
	$(CXX) -shared -o _pyIdlak_txp.so -Wl,--no-undefined -Wl,--as-needed \
		-Wl,-soname=_pyIdlak_txp.so,--whole-archive _pyIdlak_txp.a $(ADDLIBS) $(PUJIXMLROOT)/scripts/libpugixml.a -Wl,--no-whole-archive $(LDFLAGS) $(LDLIBS)
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
endif

clean_wrapper:
	-rm -rf pyIdlak_txp.py pyIdlak_txp.pyc pyIdlak_txp_wrap.cc *.pyc __pycache__
	@echo "REQUIRED FOR MAKE DO NOT DELETE!" > pyIdlak_txp_wrap.cc

clean: clean_wrapper

all: sharedlib

endif # PYIDLAK
