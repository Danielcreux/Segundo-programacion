#include <iostream>
#include <iomanip> // for std::setprecision

int main() {
    long long iterations = 1000000000; // 1 billion iterations
    double numero = 1.000000000043;

    for (long long i = 0; i < iterations; ++i) {
        numero *= 1.00000000000534;
    }

    std::cout << std::setprecision(15);
    std::cout << "Resultado después de " << iterations << " iteraciones: " << numero << std::endl;

    return 0;
}