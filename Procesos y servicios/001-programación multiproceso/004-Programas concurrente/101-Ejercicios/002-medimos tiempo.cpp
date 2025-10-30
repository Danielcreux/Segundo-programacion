#include <iostream>
#include <iomanip>
#include <chrono> // for timing

int main() {
    long long iterations = 10000000000; // 1 billion iterations
    double numero = 1.000000000043;

    // Record start time
    auto start = std::chrono::high_resolution_clock::now();

    for (long long i = 0; i < iterations; ++i) {
        numero *= 1.00000000000534;
    }

    // Record end time
    auto end = std::chrono::high_resolution_clock::now();

    // Compute duration in seconds
    std::chrono::duration<double> duration = end - start;

    std::cout << std::setprecision(15);
    std::cout << "Resultado después de " << iterations << " iteraciones: " << numero << std::endl;
    std::cout << "Tiempo transcurrido: " << duration.count() << " segundos" << std::endl;

    return 0;
}
