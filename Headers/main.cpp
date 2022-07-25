/* -----------------------------------------------------------------
  Starting code for a sort comparison assignment. Original 
  source: Gaddis Book: 
  Chapter 7: Programming Challenge #7
  Updated by Dr. Byun & Dr. Gross for CST238.

-------------------------------------------------------------------*/


#include <iostream>
#include <fstream>
#include <time.h>
#include "header.h"
using namespace std;

// Function prototypes
int * readNumbers(string filename, int & size);
int * genNumbers(int size);

int main(int argc, char *argv[]) { 

    int size = 0;
    if (argc > 1) {
       size = atoi(argv[1]);
    }
    char sortType = 'b';
    if (argc > 2) {
       sortType = argv[2][0];
    }
    bool verbose = true;
    if (argc > 3) {
//        verbose = (argv[3] == "false" | argv[3] == "quiet" | argv[3] == "f") ? false : true;
        verbose = (argv[3] == "false" || argv[3] == "quiet");
    }
    cout << boolalpha << "Verbose: " << verbose << noboolalpha << endl;

    // string filename;
    // cin >> filename;
    // filename = "ten_thousand_numbers.txt";
    // Read the numbers into the array.
    // int * a = readNumbers(filename, size);
    int * a = genNumbers(size);

    switch (sortType) {
       case 'b':
          bubble_sort(a, size, false);
          break;
       case 'i':
          insertion_sort(a, size, false);
          break;
       case 'f':
          fast_insertion_sort(a, size, false);
          break;
       case 's':
          selection_sort(a, size, false);
          break;
       case 'h':
          heap_sort(a, size, false);
          break;
       case 'm':
          merge_sort(a, size, false);
          break;
       case 'q':
          quick_sort(a, size, false);
          break;
       default:
          break;
    }

    return 0;
}
int * genNumbers(int size) {
  // intentionally not seeding PRNG
  int * a = new int[size];
  for(int i = 0; i < size; i++) {
    a[i] = rand()%size;
  }
  return a;
}


// ********************************************************
// The readNumbers function reads numbers from inFile and *
// stores them in the numbers array.                      *
// ********************************************************
int * readNumbers(string filename, int & size) {
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
    int * a = new int[size];
    for (int i = 0; i < size; i++) {
        inFile >> a[i];
    }
    return a;
}
