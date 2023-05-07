#include "mysorts.h"
#include <fstream>
#include <iostream>
#include <time.h>
#include <string>
using namespace std;

const string FILEPATH="Source/test_238/";

// Function prototypes
int *readNumbers(int &size);

int main(int argc, char *argv[]) { 
	int size = 250000;
    if (argc > 1) {
       size = atoi(argv[1]);
    }

    char sortType = 'b';
    if (argc > 2) {
       sortType = argv[2][0];
    }

    bool verbose = true;
    if (argc > 3) {
        string input = argv[3];
        int strCmpResult = input.compare("false");
        verbose = (strCmpResult == 0) ? false : true;
    }
    
    if (verbose){
        cout << boolalpha << "Verbose: " << verbose << noboolalpha << endl;
    }

   int *a = readNumbers(size);

    switch (sortType) {
       case 'b':
          bubble_sort(a, size);
          break;
       case 'i':
          insertion_sort(a, size);
          break;
       case 'f':
          fast_insertion_sort(a, size);
          break;
       case 's':
          selection_sort(a, size);
          break;
       /*case 'h':
          heap_sort(a, size);
          break;
       case 'm':
          merge_sort(a, size);
          break;
       case 'q':
          quick_sort(a, size);
          break;*/
       default:
          break;
    }


	return 0;
}

// ********************************************************
// The readNumbers function reads numbers from inFile and *
// stores them in the numbers array.                      *
// ********************************************************
int *readNumbers(int &size) {
	// File stream object
	ifstream inFile;
  string filename = FILEPATH + to_string(size) + ".txt";

	// Open the input file.
	inFile.open(filename);

	// Test for errors.
	if (inFile.fail()) {
		cout << "Error opening the file " + filename + ".\n";
		exit(1);
	}

	inFile >> size;
	// Array to hold the numbers
	int *a = new int[size];
	for (int i = 0; i < size; i++) {
		inFile >> a[i];
	}
	return a;
}

