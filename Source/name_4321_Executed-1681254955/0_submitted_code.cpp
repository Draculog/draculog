#include "header.h"
#include <iostream>
#include <time.h>
using namespace std;

void swap(int *values, int i1, int i2) {
	int temp = values[i1];
	values[i1] = values[i2];
	values[i2] = temp;
}

bool isSorted(int *values, int size) {
	for (int i = 0; i < size - 1; i++) {
		if (values[i] > values[i + 1]) {
			return false;
		}
	}
	return true;
}

int *copyArray(int *source, int size) {
	int *copy = new int[size];
	for (int i = 0; i < size; i++) {
		copy[i] = source[i];
	}
	return copy;
}

void bubble_sort(int *values, int size) {
	long long int comps = 0;
	long long int swaps = 0;
	clock_t startClock;
	clock_t elapsedTime;

	cout << "Start the bubble sorting..." << endl;
	// Measure the starting clock and conduct the bubble sorting
	startClock = clock();
	// sorting code goes here
	for (int i = 0; i < size - 1; i++) {
		for (int k = 0; k < size - i - 1; k++) {
#ifdef COUNT
			comps++;
#endif
			if (values[k] > values[k + 1]) {
				swap(values, k, k + 1);
#ifdef COUNT
				swaps++;
#endif
			}
		}
	}

	elapsedTime = clock() - startClock;
	cout << "Bubble sort completed. Is sorted: " << boolalpha
		 << isSorted(values, size) << endl;
	cout << "Elapsed time: " << (((double)elapsedTime) / CLOCKS_PER_SEC)
		 << " seconds" << endl;
#ifdef COUNT
	cout << "Swaps: " << swaps << endl;
	cout << "Comps: " << comps << endl << endl;
#endif
}

void insertion_sort(int *values, int size) {
	long long int comps = 0;
	long long int swaps = 0;
	clock_t startClock;
	clock_t elapsedTime;

	cout << "Start the insertion sorting..." << endl;
	// Measure the starting clock and conduct the bubble sorting
	startClock = clock();
	// sorting code goes here
	for (int i = 1; i < size; i++) {
		for (int k = i; k > 0; k--) {
#ifdef COUNT
			comps++;
#endif
			if (values[k] < values[k - 1]) {
#ifdef COUNT
				swaps++;
#endif
				swap(values, k, k - 1);
			} else {
				break;
			}
		}
	}

	elapsedTime = clock() - startClock;
	cout << "Insertion sort completed. Is sorted: " << boolalpha
		 << isSorted(values, size) << endl;
	cout << "Elapsed time: " << (((double)elapsedTime) / CLOCKS_PER_SEC)
		 << " seconds" << endl;
#ifdef COUNT
	cout << "Swaps: " << swaps << endl;
	cout << "Comps: " << comps << endl << endl;
#endif
}

void selection_sort(int *values, int size) {
	long long int comps = 0;
	long long int swaps = 0;
	clock_t startClock;
	clock_t elapsedTime;

	cout << "Start the selection sorting..." << endl;
	// Measure the starting clock and conduct the bubble sorting
	startClock = clock();
	// sorting code goes here
	for (int i = 0; i < size - 1; i++) {
		int minIndex = i;
		for (int k = i + 1; k < size; k++) {
#ifdef COUNT
			comps++;
#endif
			if (values[k] < values[minIndex]) {
				minIndex = k;
			}
		}
		if (i != minIndex) {
#ifdef COUNT
			swaps++;
#endif
			swap(values, i, minIndex);
		}
	}

	elapsedTime = clock() - startClock;
	cout << "Selection sort completed. Is sorted: " << boolalpha
		 << isSorted(values, size) << endl;
	cout << "Elapsed time: " << (((double)elapsedTime) / CLOCKS_PER_SEC)
		 << " seconds" << endl;
#ifdef COUNT
	cout << "Swaps: " << swaps << endl;
	cout << "Comps: " << comps << endl << endl;
#endif
}

void fast_insertion_sort(int *values, int size) {
	long long int comps = 0;
	long long int swaps = 0;
	clock_t startClock;
	clock_t elapsedTime;

	cout << "Start the fast insertion sorting..." << endl;
	// Measure the starting clock and conduct the bubble sorting
	startClock = clock();
	// sorting code goes here
	for (int i = 1; i < size; i++) {
		int finalLocation = i;
		for (int k = i - 1; k >= 0; k--) {
#ifdef COUNT
			comps++;
#endif
			// if out of order
			if (values[i] < values[k]) {
				// move final location back one
				finalLocation--;
			} else {
				// otherwise we're done
				break;
			}
		}
		// if we need to shift
		if (finalLocation != i) {
			// copy off temp value
			int temp = values[i];
			// shift everything up
			for (int s = i; s > finalLocation; s--) {
				values[s] = values[s - 1];
			}
#ifdef COUNT
			swaps += i - finalLocation;
#endif
			// put temp in right location
			values[finalLocation] = temp;
		}
	}

	elapsedTime = clock() - startClock;
	cout << "Fast insertion sort completed. Is sorted: " << boolalpha
		 << isSorted(values, size) << endl;
	cout << "Elapsed time: " << (((double)elapsedTime) / CLOCKS_PER_SEC)
		 << " seconds" << endl;
#ifdef COUNT
	cout << "Swaps: " << swaps / 3 << endl;
	cout << "Comps: " << comps << endl << endl;
#endif
}
