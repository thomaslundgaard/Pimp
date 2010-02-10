UI_FILES=$(shell ls src/*.ui 2>/dev/null)
UI_COMPILED=$(UI_FILES:.ui=_ui.py)
QRC_FILES=$(shell ls src/*.qrc 2>/dev/null)
QRC_COMPILED=$(QRC_FILES:.qrc=_rc.py)
PY_FILES=$(shell ls src/*.py 2>/dev/null)
#PY_COMPILED=$(PY_FILES:.py=.pyc)

prefix=/usr
INSTALLDIR=$(prefix)/share/pympdjuke
INSTALL_FILES=$(PY_FILES) $(PY_COMPILED) $(shell ls resources/* pixmaps/*)

all: build

build: $(UI_COMPILED) $(QRC_COMPILED) $(PY_COMPILED)

run: $(UI_COMPILED) $(QRC_COMPILED)
	python src/main.py

install: build uninstall
	@ for file in $(INSTALL_FILES); do \
		mkdir -p "$(INSTALLDIR)/$$(dirname $$file)"; \
		install "$$file" "$(INSTALLDIR)/$$(dirname $$file)"; \
	done
	chmod a+x "$(INSTALLDIR)/src/main.py"
	ln -s "$(INSTALLDIR)/src/main.py" "$(prefix)/bin/pympdjuke"
	mkdir -p "$(prefix)/share/applications/"
	install "pympdjuke.desktop" "$(prefix)/share/applications/"
	xdg-icon-resource install pixmaps/icon16.png --novendor --size 16 pympdjuke
	xdg-icon-resource install pixmaps/icon48.png --novendor --size 48 pympdjuke
	xdg-icon-resource install pixmaps/icon128.png --novendor --size 128 pympdjuke

uninstall:
	- rm -r "$(INSTALLDIR)" "$(prefix)/bin/pympdjuke" "$(prefix)/share/applications/pympdjuke.desktop"
	- xdg-icon-resource uninstall --size 16 pympdjuke
	- xdg-icon-resource uninstall --size 48 pympdjuke
	- xdg-icon-resource uninstall --size 128 pympdjuke

clean:
	find . -name *.pyc -exec rm -f "{}" \;
	find . -name *_ui.py -exec rm -f "{}" \;
	find . -name *_rc.py -exec rm -f "{}" \;

%.pyc:%.py
	# compile python files
	#python -o "$@" "$<" 

%_ui.py:%.ui
	pyuic4 -o "$@" "$<"

%_rc.py:%.qrc
	pyrcc4 -o "$@" "$<"

.PHONY: run install uninstall clean build

