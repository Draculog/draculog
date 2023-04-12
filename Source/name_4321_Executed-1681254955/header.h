#ifndef MYSORTS_H
#define MYSORTS_H
int * copyArray(int * values, int size);
void bubble_sort (int * values, int size);
void insertion_sort (int * values, int size);
void fast_insertion_sort (int * values, int size);
void selection_sort (int * values, int size);
bool isSorted(int * values, int size);
void swap(int * values, int i1, int i2);
#endif