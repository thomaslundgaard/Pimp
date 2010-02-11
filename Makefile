# Programs
INSTALL="install"

UI_FILES=$(shell ls src/*.ui 2>/dev/null)
UI_COMPILED=$(UI_FILES:.ui=_ui.py)
QRC_FILES=$(shell ls src/*.qrc 2>/dev/null)
QRC_COMPILED=$(QRC_FILES:.qrc=_rc.py)
PY_FILES=$(shell ls src/*.py 2>/dev/null)
#PY_COMPILED=$(PY_FILES:.py=.pyc)

DESTDIR=/usr
INSTALLDIR=$(DESTDIR)/share/pympdjuke
INSTALL_FILES=$(PY_FILES) $(PY_COMPILED) $(shell ls resources/* pixmaps/*)


all: build

build: $(UI_COMPILED) $(QRC_COMPILED) $(PY_COMPILED)

run: $(UI_COMPILED) $(QRC_COMPILED)
	python src/main.py

install: build uninstall
	for file in $(INSTALL_FILES); do \
		dir="$(INSTALLDIR)/$$(dirname $$file)"; \
		mkdir -p "$$dir"; \
		$(INSTALL) "$$file" "$$dir"; \
	done
	# executable
	chmod a+x "$(INSTALLDIR)/src/main.py"
	mkdir -p "$(DESTDIR)/bin"
	ln -s "../share/pympdjuke/src/main.py" "$(DESTDIR)/bin/pympdjuke"
	# .desktop file
	mkdir -p "$(DESTDIR)/share/applications/"
	$(INSTALL) "pympdjuke.desktop" "$(DESTDIR)/share/applications/"
	# icons
	for file in $$(ls icons/*.png); do \
		dir="$(DESTDIR)/share/icons/hicolor/$$(basename $$file .png)/apps"; \
		mkdir -p "$$dir"; \
		$(INSTALL) "$$file" "$$dir/pympdjuke.png"; \
	done

uninstall:
	- rm -r "$(INSTALLDIR)"
	- rm -r "$(DESTDIR)/bin/pympdjuke"
	- rm -r "$(DESTDIR)/share/applications/pympdjuke.desktop"
	- find "$(DESTDIR)/share/icons/hicolor" -name "pympdjuke.*" -exec rm -f "{}" \;

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

