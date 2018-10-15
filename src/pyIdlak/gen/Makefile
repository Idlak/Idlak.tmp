
include ../../kaldi.mk

ifeq ($(PYIDLAK), true)

OBJFILES = python-gen-api.o pyIdlak_gen_wrap.o

LIBNAME = _pyIdlak_gen

ADDLIBS = ../pylib/_pyIdlak_pylib.a  ../../idlakfeat/idlak-feat.a ../../feat/kaldi-feat.a ../../transform/kaldi-transform.a \
          ../../gmm/kaldi-gmm.a ../../tree/kaldi-tree.a ../../hmm/kaldi-hmm.a \
          ../../util/kaldi-util.a ../../matrix/kaldi-matrix.a ../../base/kaldi-base.a \

EXTRA_CXXFLAGS = -fPIC -I$(PYTHONDEVINC) -I../..
EXTRA_LDLIBS =

include ../../makefiles/default_rules.mk

ifeq ($(KALDI_FLAVOR), dynamic)
  STATICLIB =
else
  STATICLIB = _pyIdlak_gen.a
endif

ifeq ($(PYTHONDEVLIBDIR),)
  PYLIBFLAG = -l$(PYTHONDEVLIB)
else
  PYLIBFLAG = -L$(PYTHONDEVLIBDIR) -l$(PYTHONDEVLIB)
endif
EXTRA_LDLIBS += $(PYLIBFLAG)

.PHONY: wrapper
wrapper:
	$(SWIG) -c++ -python -o pyIdlak_gen_wrap.cc pyIdlak_gen.i
pyIdlak_gen_wrap.o: wrapper

sharedlib: $(STATICLIB)
ifeq ($(KALDI_FLAVOR), dynamic)
  ifeq ($(shell uname), Darwin)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_gen.dylib _pyIdlak_gen.dylib
  else ifeq ($(shell uname), Linux)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_gen.so _pyIdlak_gen.so
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
else
  ifeq ($(shell uname), Darwin)
	$(CXX) -dynamiclib -o _pyIdlak_gen.dylib -install_name @rpath/_pyIdlak_gen.a $(LDFLAGS) $(LDLIBS)
  else ifeq ($(shell uname), Linux)
	# Building shared library from static (static was compiled with -fPIC)
	@echo "Building shared library from static (static was compiled with -fPIC)"
	$(CXX) -shared -o _pyIdlak_gen.so -Wl,--no-undefined -Wl,--as-needed \
		-Wl,-soname=_pyIdlak_gen.so,--whole-archive _pyIdlak_gen.a $(ADDLIBS) -Wl,--no-whole-archive \
		 $(LDFLAGS) $(LDLIBS)
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
endif

clean_wrapper:
	-rm -rf pyIdlak_gen.py pyIdlak_gen_wrap.cc *.pyc __pycache__
	@echo "REQUIRED FOR MAKE DO NOT DELETE!" > pyIdlak_gen_wrap.cc

clean: clean_wrapper

all: sharedlib

endif # PYIDLAK
