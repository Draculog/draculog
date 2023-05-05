COM = g++
FLAGS = -std=c++11 -Wno-psabi
MAIN_HEADER = main.cpp
HEADER = mysorts.h
STUDENT_CODE = 0_submitted_code.cpp

all: main

deps: $(HEADER)

main: deps $(MAIN_HEADER)
	$(COM) $(FLAGS) $(MAIN_HEADER) $(HEADER) $(STUDENT_CODE) -o sort

