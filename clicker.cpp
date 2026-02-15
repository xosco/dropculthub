#include <windows.h>
#include <atomic>
#include <thread>

// Глобальные переменные управления
std::atomic<bool> g_running(false); // Запущен ли поток вообще
std::atomic<bool> g_active(false);  // Активен ли сам клик в данный момент
std::atomic<int> g_cps(100);
std::atomic<int> g_toggleKey(VK_F6);

void SendClick() {
    INPUT inputs[2] = {};
    inputs[0].type = INPUT_MOUSE;
    inputs[0].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
    inputs[1].type = INPUT_MOUSE;
    inputs[1].mi.dwFlags = MOUSEEVENTF_LEFTUP;
    SendInput(2, inputs, sizeof(INPUT));
}

// Фоновая функция, которая будет работать в отдельном потоке
void ClickerThread() {
    LARGE_INTEGER frequency, t1, t2;
    QueryPerformanceFrequency(&frequency);
    
    bool keyWasPressed = false;

    while (g_running) {
        // Проверка клавиши переключения
        bool keyIsPressed = GetAsyncKeyState(g_toggleKey) & 0x8000;
        if (keyIsPressed && !keyWasPressed) {
            g_active = !g_active;
        }
        keyWasPressed = keyIsPressed;

        if (g_active) {
            double interval = 1.0 / g_cps;
            QueryPerformanceCounter(&t1);
            
            SendClick();

            // Прецизионное ожидание
            do {
                QueryPerformanceCounter(&t2);
            } while ((double)(t2.QuadPart - t1.QuadPart) / frequency.QuadPart < interval);
        } else {
            Sleep(10); // Разгрузка процессора
        }
    }
}

// Экспортируемые функции для Python
extern "C" {
    __declspec(dllexport) void Start(int cps, int key) {
        if (g_running) return; // Уже запущен
        g_cps = cps;
        g_toggleKey = key;
        g_running = true;
        g_active = false;
        std::thread(ClickerThread).detach(); // Запускаем в фоне
    }

    __declspec(dllexport) void Stop() {
        g_running = false;
    }

    __declspec(dllexport) bool IsActive() {
        return g_active;
    }
}