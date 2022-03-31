#include <iostream>

using namespace std;
int main(int argc, char *argv[]) {
	for (int i = 0; i < 5000000; i++){
		cout << "run: " << i <<endl;
		i++;
	}
}