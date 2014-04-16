UNAME := $(shell uname)

ifeq ($(UNAME), CYGWIN_NT-6.1-WOW64)
	OPEN = cygstart
	PYTHON="/cygdrive/c/Python27/python.exe"
endif
ifeq ($(UNAME), Darwin)
	OPEN = open
endif

all: dist

dist:
	$(PYTHON) setup.py
	sed -i 's/TkAgg/Agg/g' dist/mpl-data/matplotlibrc

installer: dist
	iscc "LM_ratio_installer.iss"

clean:
	rm -rf dist