
include ../../kaldi.mk

ifeq ($(PYIDLAK), true)

OBJFILES = python-vocoder-lib.o python-vocoder-api.o python-vocoder-mlpg.o pyIdlak_vocoder_wrap.o

LIBNAME = _pyIdlak_vocoder

# ADDLIBS = ../../idlaktxp/idlak-txp.a ../../util/kaldi-util.a ../../matrix/kaldi-matrix.a ../../base/kaldi-base.a

EXTRA_CXXFLAGS = -fPIC -I$(PYTHONDEVINC) -I$(SPTKROOT)/include
EXTRA_LDLIBS = -l$(PYTHONDEVLIB) $(SPTKROOT)/lib/libSPTK.a

include ../../makefiles/default_rules.mk

ifeq ($(KALDI_FLAVOR), dynamic)
  STATICLIB =
else
  STATICLIB = _pyIdlak_vocoder.a
endif

.PHONY: wrapper
wrapper:
	$(SWIG) -c++ -python -o pyIdlak_vocoder_wrap.cc -I$(SPTKROOT)/include pyIdlak_vocoder.i
pyIdlak_vocoder_wrap.o: wrapper

sharedlib: $(STATICLIB)
ifeq ($(KALDI_FLAVOR), dynamic)
  ifeq ($(shell uname), Darwin)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_vocoder.dylib _pyIdlak_vocoder.dylib
  else ifeq ($(shell uname), Linux)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_vocoder.so _pyIdlak_vocoder.so
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
else
  ifeq ($(shell uname), Darwin)
	$(CXX) -dynamiclib -o _pyIdlak_vocoder.dylib -install_name @rpath/_pyIdlak_vocoder.a $(LDFLAGS) $(LDLIBS)
  else ifeq ($(shell uname), Linux)
	# Building shared library from static (static was compiled with -fPIC)
	@echo "Building shared library from static (static was compiled with -fPIC)"
	$(CXX) -shared -o _pyIdlak_vocoder.so -Wl,--no-undefined -Wl,--as-needed \
		-Wl,-soname=_pyIdlak_vocoder.so,--whole-archive _pyIdlak_vocoder.a $(ADDLIBS) -Wl,--no-whole-archive \
		 $(LDFLAGS) $(LDLIBS)
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
endif

clean_wrapper:
	-rm -rf pyIdlak_vocoder.py pyIdlak_vocoder_wrap.cc *.pyc __pycache__
	@echo "REQUIRED FOR MAKE DO NOT DELETE!" > pyIdlak_vocoder_wrap.cc

clean: clean_wrapper

all: sharedlib

endif # PYIDLAK
