#include <iostream>
#include <vector>
#include <future>
#include <chrono>
#include <algorithm>
#include <cmath>
#include <mutex>

std::mutex cout_mutex; // Mutex para sincronizar la salida

int trabajo(int id) {
    double numero = 1.00000000098;
    
    // Sincronizar la salida para que sea ordenada
    {
        std::lock_guard<std::mutex> lock(cout_mutex);
        std::cout << "empiezo " << id << std::endl;
    }
    
    for (int i = 0; i < 1000000000; i++) {
        numero *= 1.0000000000654;
    }
    
    auto now = std::chrono::system_clock::now();
    auto final_time = std::chrono::duration_cast<std::chrono::seconds>(
        now.time_since_epoch());
    
    return final_time.count();
}

int main() {
    auto inicio_time = std::chrono::system_clock::now();
    auto inicio = std::chrono::duration_cast<std::chrono::seconds>(
        inicio_time.time_since_epoch()).count();
    
    std::vector<std::future<int>> futures;
    
    // Crear 16 tareas asíncronas
    for (int i = 0; i < 24; i++) {
        futures.push_back(std::async(std::launch::async, trabajo, i));
    }
    
    // Recoger los resultados
    std::vector<int> finales;
    for (auto& future : futures) {
        finales.push_back(future.get());
    }
    
    // Encontrar el tiempo final máximo
    int final = *std::max_element(finales.begin(), finales.end());
    
    std::cout << "he tardado " << (final - inicio) << " segundos" << std::endl;
    
    return 0;
}
