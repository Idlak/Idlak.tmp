
include ../../kaldi.mk

ifeq ($(PYIDLAK), true)

OBJFILES = python-vocode-api.o pyIdlak_vocode_wrap.o

LIBNAME = _pyIdlak_vocode

# ADDLIBS = ../../idlaktxp/idlak-txp.a ../../util/kaldi-util.a ../../matrix/kaldi-matrix.a ../../base/kaldi-base.a

EXTRA_CXXFLAGS = -fPIC -I$(PYTHONDEVINC) -I$(SPTKROOT)/include
EXTRA_LDLIBS = -lpython2.7 $(SPTKROOT)/lib/libSPTK.a

include ../../makefiles/default_rules.mk

ifeq ($(KALDI_FLAVOR), dynamic)
  STATICLIB =
else
  STATICLIB = _pyIdlak_vocode.a
endif

.PHONY: wrapper
wrapper:
	$(SWIG) -c++ -python -o pyIdlak_vocode_wrap.cc -I$(SPTKROOT)/include pyIdlak_vocode.i
pyIdlak_vocode_wrap.o: wrapper

sharedlib: $(STATICLIB)
ifeq ($(KALDI_FLAVOR), dynamic)
  ifeq ($(shell uname), Darwin)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_vocode.dylib _pyIdlak_vocode.dylib
  else ifeq ($(shell uname), Linux)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_vocode.so _pyIdlak_vocode.so
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
else
  ifeq ($(shell uname), Darwin)
	$(CXX) -dynamiclib -o _pyIdlak_vocode.dylib -install_name @rpath/_pyIdlak_vocode.a $(LDFLAGS) $(LDLIBS)
  else ifeq ($(shell uname), Linux)
	# Building shared library from static (static was compiled with -fPIC)
	@echo "Building shared library from static (static was compiled with -fPIC)"
	$(CXX) -shared -o _pyIdlak_vocode.so -Wl,--no-undefined -Wl,--as-needed \
		-Wl,-soname=_pyIdlak_vocode.so,--whole-archive _pyIdlak_vocode.a $(ADDLIBS) -Wl,--no-whole-archive \
		 $(LDFLAGS) $(LDLIBS)
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
endif

clean_wrapper:
	-rm -f pyIdlak_vocode.py pyIdlak_vocode.pyc pyIdlak_vocode_wrap.cc *.pyc
	@echo "REQUIRED FOR MAKE DO NOT DELETE!" > pyIdlak_vocode_wrap.cc

clean: clean_wrapper

all: sharedlib

endif # PYIDLAK