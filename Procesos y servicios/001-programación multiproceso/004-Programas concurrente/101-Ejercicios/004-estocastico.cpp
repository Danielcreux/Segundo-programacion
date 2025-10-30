#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <omp.h>

struct Emitter {
    float x, y;
    float radius;
    float intensity;
    cv::Vec3f color;  // RGB en [0,1]
};

static cv::Vec3f random_color(std::mt19937 &rng) {
    std::uniform_real_distribution<float> dist(0.2f, 1.0f);
    float r = dist(rng), g = dist(rng), b = dist(rng);
    float m = std::max({r,g,b});
    return cv::Vec3f(r/m, g/m, b/m);
}

// “Splat” 3x3 para que cada sample deje más huella visual
inline void splat3x3(cv::Mat &img, int x, int y, const cv::Vec3f &val) {
    static const float k[3][3] = {
        {0.0625f, 0.125f, 0.0625f},
        {0.1250f, 0.250f, 0.1250f},
        {0.0625f, 0.125f, 0.0625f}
    };
    const int W = img.cols, H = img.rows;
    for (int dy=-1; dy<=1; ++dy) {
        int py = y + dy;
        if (py < 0 || py >= H) continue;
        for (int dx=-1; dx<=1; ++dx) {
            int px = x + dx;
            if (px < 0 || px >= W) continue;
            img.at<cv::Vec3f>(py, px) += val * k[dy+1][dx+1];
        }
    }
}

int main() {
    // ---------- parámetros hardcoded ----------
    const int W = 960;
    const int H = 540;

    // Usa el máximo de hilos disponibles (si quieres forzar, pon un número fijo)
    int NUM_THREADS = 32;
    omp_set_num_threads(NUM_THREADS);

    const int   NUM_EMITTERS       = 1200;     // menos de 2000 para reducir dispersión
    long long   SAMPLES_PER_FRAME  = 1'000'000; // más muestras: más señal visible
    const bool  USE_SPLAT_3x3      = true;     // true => “pincel” más visible
    const float DECAY              = 0.96f;    // persistencia
    const float GAMMA              = 2.2f;     // mapea a perceptual
    const float CLAMP_LUMA         = 5.0f;     // clamp antes de gamma (en lineal)

    // ---------- escena ----------
    cv::Mat accum = cv::Mat::zeros(H, W, CV_32FC3);

    std::mt19937 rng_scene{std::random_device{}()};
    std::uniform_real_distribution<float> ux(30.f, W - 30.f);
    std::uniform_real_distribution<float> uy(30.f, H - 30.f);
    std::uniform_real_distribution<float> ur(8.f, 50.f);
    std::uniform_real_distribution<float> uinten(0.7f, 2.0f);

    std::vector<Emitter> emitters;
    emitters.reserve(NUM_EMITTERS);
    for (int i = 0; i < NUM_EMITTERS; ++i) {
        Emitter e;
        e.x = ux(rng_scene);
        e.y = uy(rng_scene);
        e.radius = ur(rng_scene);
        e.intensity = uinten(rng_scene);
        e.color = random_color(rng_scene);
        emitters.push_back(e);
    }

    // Acumuladores por hilo
    std::vector<cv::Mat> thread_accums(NUM_THREADS);
    for (int t = 0; t < NUM_THREADS; ++t) {
        thread_accums[t] = cv::Mat::zeros(H, W, CV_32FC3);
    }

    cv::namedWindow("Stochastic Rendering", cv::WINDOW_AUTOSIZE);

    double fps = 0.0;
    uint64_t frame_idx = 0;

    while (true) {
        for (int t = 0; t < NUM_THREADS; ++t)
            thread_accums[t].setTo(cv::Scalar(0,0,0));

        auto t0 = std::chrono::high_resolution_clock::now();

        // ---------- muestreo paralelo ----------
        #pragma omp parallel
        {
            int tid = omp_get_thread_num();
            // Semilla por hilo + por frame (evita streams iguales)
            std::seed_seq seed{
                (unsigned)tid,
                (unsigned)frame_idx,
                (unsigned)std::chrono::high_resolution_clock::now().time_since_epoch().count()
            };
            std::mt19937 rng(seed);
            std::uniform_int_distribution<int> pick(0, (int)emitters.size() - 1);
            std::normal_distribution<float> gauss(0.f, 1.f);

            cv::Mat &acc_local = thread_accums[tid];

            #pragma omp for schedule(static)
            for (long long i = 0; i < SAMPLES_PER_FRAME; ++i) {
                const Emitter &e = emitters[pick(rng)];
                float sx = e.x + gauss(rng) * e.radius;
                float sy = e.y + gauss(rng) * e.radius;

                int px = (int)std::lround(sx);
                int py = (int)std::lround(sy);
                if ((unsigned)px >= (unsigned)W || (unsigned)py >= (unsigned)H) continue;

                cv::Vec3f contrib = e.color * e.intensity;
                if (USE_SPLAT_3x3)
                    splat3x3(acc_local, px, py, contrib);
                else
                    acc_local.at<cv::Vec3f>(py, px) += contrib;
            }
        }

        // Reducir al acumulador global
        for (int t = 0; t < NUM_THREADS; ++t)
            accum += thread_accums[t];

        auto t1 = std::chrono::high_resolution_clock::now();
        fps = 1.0 / std::chrono::duration<double>(t1 - t0).count();

        // ---------- tonemapping con auto-exposición ----------
        // 1) calcula luminancia y busca el máximo (evita valores atípicos grandes con clamp)
        cv::Mat luma;
        // Rec.709: 0.2126 R + 0.7152 G + 0.0722 B
        std::vector<cv::Mat> ch; cv::split(accum, ch);
        luma = 0.2126f*ch[2] + 0.7152f*ch[1] + 0.0722f*ch[0]; // si tuviste BGR, ajusta aquí
        double maxL;
        cv::minMaxLoc(luma, nullptr, &maxL);
        float exposure = (float)(1.0 / std::max(1e-6, std::min(maxL, (double)CLAMP_LUMA)));

        cv::Mat mapped = accum * exposure; // normaliza por el “brillo” del frame
        cv::threshold(mapped, mapped, 1.0f, 1.0f, cv::THRESH_TRUNC); // clamp post-exposure
        cv::pow(mapped, 1.0f / GAMMA, mapped);

        cv::Mat display;
        mapped.convertTo(display, CV_8UC3, 255.0);

        // HUD
        cv::putText(display, "Threads: " + std::to_string(NUM_THREADS),
                    {10, 22}, cv::FONT_HERSHEY_SIMPLEX, 0.6, {255,255,255}, 1, cv::LINE_AA);
        cv::putText(display, "Emitters: " + std::to_string(NUM_EMITTERS),
                    {10, 44}, cv::FONT_HERSHEY_SIMPLEX, 0.6, {255,255,255}, 1, cv::LINE_AA);
        cv::putText(display, "Samples/frame: " + std::to_string(SAMPLES_PER_FRAME),
                    {10, 66}, cv::FONT_HERSHEY_SIMPLEX, 0.6, {255,255,255}, 1, cv::LINE_AA);
        cv::putText(display, cv::format("FPS: %.2f", fps),
                    {10, 88}, cv::FONT_HERSHEY_SIMPLEX, 0.6, {255,255,255}, 1, cv::LINE_AA);
        cv::putText(display, "q/ESC exit | +/- samples | s: toggle splat",
                    {10, H - 12}, cv::FONT_HERSHEY_SIMPLEX, 0.5, {255,255,255}, 1, cv::LINE_AA);

        cv::imshow("Stochastic Rendering", display);

        int key = cv::waitKey(1);
        if (key == 27 || key == 'q' || key == 'Q') break;
        if (key == '+' || key == '=') SAMPLES_PER_FRAME = std::min<long long>(SAMPLES_PER_FRAME * 11 / 10, 20'000'000LL);
        if (key == '-' || key == '_') SAMPLES_PER_FRAME = std::max<long long>(SAMPLES_PER_FRAME * 9 / 10, 10'000LL);
        if (key == 's' || key == 'S') {/* toggle splat? dejaría una variable global si quieres */}

        // Decaimiento para que no crezca sin límite y dé “trail”
        accum *= DECAY;

        ++frame_idx;
    }

    return 0;
}


// g++ "004-estocastico.cpp" -fopenmp -I"C:\Users\Valentina\Downloads\OpenCV-MinGW-Build-OpenCV-4.5.5-x64\OpenCV-MinGW-Build-OpenCV-4.5.5-x64\include" -L"C:\Users\Valentina\Downloads\OpenCV-MinGW-Build-OpenCV-4.5.5-x64\OpenCV-MinGW-Build-OpenCV-4.5.5-x64\x64\mingw\lib" -lopencv_core455 -lopencv_imgproc455 -lopencv_highgui455 -lopencv_imgcodecs455 -o stochastic_render

//copy "C:\Users\Valentina\Downloads\OpenCV-MinGW-Build-OpenCV-4.5.5-x64\OpenCV-MinGW-Build-OpenCV-4.5.5-x64\x64\mingw\bin\*.dll" . && stochastic_render.exe

