UI_FILES=$(shell ls *.ui)
UI_COMPILED=$(UI_FILES:.ui=_ui.py)
QRC_FILES=$(shell ls *.qrc)
QRC_COMPILED=$(QRC_FILES:.qrc=_rc.py)

all: $(UI_COMPILED) $(QRC_COMPILED)
	python main.py

%_ui.py:%.ui
	pyuic4 -o $@ $<

%_rc.py:%.qrc
	pyrcc4 -o $@ $<
