/* -----------------------------------------------------------------
  Starting code for a sort comparison assignment. Original
  source: Gaddis Book:
  Chapter 7: Programming Challenge #7
  Updated by Dr. Byun & Dr. Gross for CST238.

-------------------------------------------------------------------*/
#define COUNT
#include "header.h"
#include <fstream>
#include <iostream>
#include <time.h>
using namespace std;

// Function prototypes
int *readNumbers(string filename, int &size);
void writeNumbers(int *numbers, int &size);
int *genNumbers(int size);

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

#ifdef COUNT
	int *a = genNumbers(size);
	// write numbers
	writeNumbers(a, size);
#endif

#ifndef COUNT
	int *a = readNumbers("previous_test.txt", size);
#endif

    // string filename;
    // cin >> filename;
    // filename = "ten_thousand_numbers.txt";
    // Read the numbers into the array.
    // int * a = readNumbers(filename, size);
    // int * a = genNumbers(size);

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
       /* case 'h':
          heap_sort(a, size);
          break;
       case 'm':
          merge_sort(a, size);
          break;
       case 'q':
          quick_sort(a, size);
          break; */
       default:
          break;
    }


	return 0;
}

int *genNumbers(int size) {
	// intentionally not seeding PRNG
	int *a = new int[size];
	for (int i = 0; i < size; i++) {
		a[i] = rand() % size;
	}
	return a;
}

// ********************************************************
// The readNumbers function reads numbers from inFile and *
// stores them in the numbers array.                      *
// ********************************************************
int *readNumbers(string filename, int &size) {
	// File stream object
	ifstream inFile;

	// Open the input file.
	inFile.open(filename);

	// Test for errors.
	if (!inFile) {
		cout << "Error opening the file.\n";
		return 0;
	}

	inFile >> size;
	// Array to hold the numbers
	int *a = new int[size];
	for (int i = 0; i < size; i++) {
		inFile >> a[i];
	}
	return a;
}

// stores an array of numbers in a file called previous_test.txt
void writeNumbers(int *numbers, int &size) {
	// File stream object
	ofstream outFile;

	// Open the input file.
	outFile.open("previous_test.txt");

	// Test for errors.
	if (!outFile) {
		cout << "Error opening the file.\n";
		return;
	}

	outFile << size << "\n";
	for (int i = 0; i < size; i++) {
		outFile << numbers[i] << "\n";
	}
	return;
}
