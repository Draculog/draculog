#ifndef HEADER_H
#define HEADER_H
int * copyArray(int * values, int size);

void print(int * a, int size);

void bubble_sort (int * values, int size);
void insertion_sort (int * values, int size);
void fast_insertion_sort (int * values, int size);
void selection_sort (int * values, int size);

// for heap sort
void heapify(int * arr, int n, int i);
void heapSortRecurse(int * arr, int n);
void heap_sort(int * values, int size);

// for merge sort
void merge(int * values, int l, int m, int r);
void merge_sort_recurse(int * values, int l, int r);
void merge_sort(int * values, int size);

// for quick sort
int partition(int * arr, int l, int h);
void quickSortRecurse(int * arr, int l, int h);
void quick_sort(int * values, int size);

bool isSorted(int * values, int size);
void swap(int * values, int i1, int i2);
#endif
