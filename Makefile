UI_FILES=$(shell ls src/*.ui 2>/dev/null)
UI_COMPILED=$(UI_FILES:.ui=_ui.py)
QRC_FILES=$(shell ls src/*.qrc 2>/dev/null)
QRC_COMPILED=$(QRC_FILES:.qrc=_rc.py)
PY_FILES=$(shell ls src/*.py 2>/dev/null)
PY_COMPILED=$(PY_FILES:.py=.pyc)

prefix=/usr
INSTALLDIR=$(prefix)/share/pympdjuke
INSTALL_FILES=$(PY_FILES) $(PY_COMPILED) $(shell ls resources/* pixmaps/*)

all: build
   
run: build
	python src/main.py

install: clean build $(PY_COMPILED)
	@ for file in $(INSTALL_FILES); do \
		mkdir -p "$(INSTALLDIR)/$$(dirname $$file)"; \
		install "$$file" "$(INSTALLDIR)/$$(dirname $$file)"; \
	done
	chmod a+x "$(INSTALLDIR)/src/main.py"
	ln -s "$(INSTALLDIR)/src/main.py" "$(prefix)/bin/pympdjuke"

uninstall:
	rm -r $(INSTALLDIR) "$(prefix)/bin/pympdjuke"

clean:
	rm -f src/*_ui.py src/*_rc.py src/*.pyc

build: $(UI_COMPILED) $(QRC_COMPILED)

%.pyc:%.py
	cp $< $@

%_ui.py:%.ui
	pyuic4 -o $@ $<

%_rc.py:%.qrc
	pyrcc4 -o $@ $<

.PHONY: run install clean build
