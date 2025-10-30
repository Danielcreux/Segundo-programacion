#include <iostream>
#include <iomanip>
#include <chrono>
#include <cmath>
#include <omp.h>

int main() {
    // ⚠️ This is 10 billion (not 1 billion)
    long long iterations = 10000000000000000LL; 
    const double factor  = 1.00000000000534;
    const double initial = 1.000000000043;

    // Time start
    auto start = std::chrono::high_resolution_clock::now();

    // Parallel: split the exponent across threads and multiply partial powers.
    double combined_power = 1.0;

    #pragma omp parallel
    {
        int T = omp_get_num_threads();
        int tid = omp_get_thread_num();

        // Divide iterations as evenly as possible across threads
        long long base_chunk = iterations / T;
        long long remainder  = iterations % T;
        long long my_count   = base_chunk + (tid < remainder ? 1 : 0);

        // Each thread computes factor^my_count (use pow for speed)
        double local_power = std::pow(factor, static_cast<double>(my_count));

        // Multiplicative reduction
        #pragma omp atomic
        combined_power *= local_power;
    }

    double numero = initial * combined_power;

    // Time end
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    std::cout << std::setprecision(15);
    std::cout << "Resultado después de " << iterations << " iteraciones: " << numero << "\n";
    std::cout << "Tiempo transcurrido: " << duration.count() << " segundos\n";

    return 0;
}
// g++ -fopenmp "003-openmp.cpp" -o a.out
