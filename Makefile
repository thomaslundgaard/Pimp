UIFILES=$(shell ls *.ui)
COMPILEDUI=$(UIFILES:.ui=.py)

all: $(COMPILEDUI)
	python main.py

%.py:%.ui
	pyuic4 -o $@ $<

