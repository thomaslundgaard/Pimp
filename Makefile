UI_FILES=$(shell ls *.ui 2>/dev/null)
UI_COMPILED=$(UI_FILES:.ui=_ui.py)
QRC_FILES=$(shell ls *.qrc 2>/dev/null)
QRC_COMPILED=$(QRC_FILES:.qrc=_rc.py)

all: $(UI_COMPILED) $(QRC_COMPILED)
	python main.py

clean:
	rm -f *_ui.py *_rc.py *.pyc

%_ui.py:%.ui
	pyuic4 -o $@ $<

%_rc.py:%.qrc
	pyrcc4 -o $@ $<
