COM = g++
FLAGS = -std=c++11 -Wno-psabi
FILES = -1_submitted_code.cpp
MAIN_HEADER = main.cpp
HEADER = header.h

all: main

deps: $(HEADER)

main: deps $(MAIN_HEADER)
	$(COM) $(FLAGS) $(MAIN_HEADER) $(FILES) -o code

