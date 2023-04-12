#include <time.h>
#include <iostream>
#include "header.h"
using namespace std;
// Sort an array of integer values in ascending order.
void bubble_sort (int * values, const int size, bool verbose) {
    int comps = 0;
    int swaps = 0;
    clock_t startClock;
    clock_t elapsedTime;
    
    cout << "Start the bubble sorting..." << endl;
    // Measure the starting clock and conduct the bubble sorting
    startClock = clock();
    for(int i = 0; i < size - 1; i++) {
        for (int k = 0; k < size - i - 1; k++) {
            comps++;
            if(values[k] > values[k+1]) {
                swaps++;
                swap(values, k, k + 1);
            }
        }
    }


    elapsedTime = clock() - startClock;
    cout << "Bubble sort completed. Is sorted: " << boolalpha <<
        isSorted(values, size) << endl;
    cout << "Elapsed time: " << (((double)elapsedTime)/CLOCKS_PER_SEC) 
        << " seconds" << endl;
    cout << "Swaps: " << swaps << endl;
    cout << "Comps: " << comps << endl << endl;
}

// Sort an array of integer values in ascending order.
void selection_sort (int * values, const int size, bool verbose) {
    int comps = 0;
    int swaps = 0;
    clock_t startClock;
    clock_t elapsedTime;
    
    cout << "Start the selection sorting..." << endl;
    // Measure the starting clock and conduct the bubble sorting
    startClock = clock();
    for (int i = 0; i < size - 1; i++) {
        int min_index = i;
        for (int k = i + 1; k < size; k++) {
            comps++;
            if(values[k] < values[min_index]) {
                min_index = k;
            }
        }
        if(i != min_index) {
            swaps++;
            swap(values, i, min_index);
        }
    }

    elapsedTime = clock() - startClock;
    cout << "Selection sort completed. Is sorted: " << boolalpha <<
        isSorted(values, size) << endl;
    cout << "Elapsed time: " << (((double)elapsedTime)/CLOCKS_PER_SEC) 
        << " seconds" << endl;
    cout << "Swaps: " << swaps << endl;
    cout << "Comps: " << comps << endl << endl;
}

// Sort an array of integer values in ascending order.
void insertion_sort (int * values, const int size, bool verbose) {
    int comps = 0;
    int swaps = 0;
    clock_t startClock;
    clock_t elapsedTime;
    
    cout << "Start the insertion sorting..." << endl;
    // Measure the starting clock and conduct the bubble sorting
    startClock = clock();
    for(int i = 1; i < size; i++) {
        for (int k = i; k > 0; k--) {
            comps++;
            if(values[k] < values[k-1]) {
                swaps++;
                swap(values, k, k - 1);
            } else {
                break;
            }
        }
    }

    elapsedTime = clock() - startClock;
    cout << "Insertion sort completed. Is sorted: " << boolalpha <<
        isSorted(values, size) << endl;
    cout << "Elapsed time: " << (((double)elapsedTime)/CLOCKS_PER_SEC) 
        << " seconds" << endl;
    cout << "Swaps: " << swaps << endl;
    cout << "Comps: " << comps << endl << endl;
}

// Sort an array of integer values in ascending order.
void fast_insertion_sort (int * values, const int size, bool verbose) {
    int comps = 0;
    int swaps = 0;
    clock_t startClock;
    clock_t elapsedTime;
    
    cout << "Start the fast insertion sorting..." << endl;
    // Measure the starting clock and conduct the bubble sorting
    startClock = clock();
    int k = 0;
    for(int i = 1; i < size; i++) {
        int x = values[i]; 
        for (k = i - 1; k >= 0; k--) {
            comps++;
            if(values[k] > x) {
                swaps++;
                values[k+1] = values[k];
            } else {
                break;
            }
        }
        swaps++;
        values[k+1] = x;

    }

    swaps /= 3; // these are only third-swaps
    elapsedTime = clock() - startClock;
    cout << "Fast insertion sort completed. Is sorted: " << boolalpha <<
        isSorted(values, size) << endl;
    cout << "Elapsed time: " << (((double)elapsedTime)/CLOCKS_PER_SEC) 
        << " seconds" << endl;
    cout << "Swaps: " << swaps << endl;
    cout << "Comps: " << comps << endl << endl;
}

bool isSorted(int * values, int size) {
    for(int i = 0; i < size - 1; i++) {
        // if(i < 10) cout << values[i] << endl;
        if(values[i] > values[i+1]) {
            return false;
        }
    }
    return true;
}

int * copyArray(int * source, int size) {
    int * dest = new int[size];
    for(int i = 0; i < size; i++) {
        dest[i] = source[i];
    }
    return dest;
}

void swap(int * values, int i1, int i2) {
    int t = values[i1];
    values[i1] = values[i2];
    values[i2] = t;
}
