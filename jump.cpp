#include <windows.h>
#include <process.h>

bool threadRunning = false; 
int targetKey = VK_SPACE; 
int jumpDelay = 20; // Оптимальная задержка для Evade

// Низкоуровневая эмуляция прыжка
void sendPerfectJump() {
    INPUT inputs[2] = {0};

    // 1. Команда: ОТПУСТИТЬ ПРОБЕЛ (чтобы сбросить физическое зажатие)
    inputs[0].type = INPUT_KEYBOARD;
    inputs[0].ki.wScan = 0x39; // Скан-код пробела
    inputs[0].ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;

    // 2. Команда: НАЖАТЬ ПРОБЕЛ
    inputs[1].type = INPUT_KEYBOARD;
    inputs[1].ki.wScan = 0x39;
    inputs[1].ki.dwFlags = KEYEVENTF_SCANCODE;

    // Отправляем обе команды мгновенно в одном пакете
    // Это заставляет игру зафиксировать новый прыжок даже при зажатом W
    SendInput(2, inputs, sizeof(INPUT));
}

void BhopThread(void* arg) {
    while (threadRunning) {
        // Проверяем, зажата ли клавиша бинда ( Space, Shift или Ctrl )
        if (GetAsyncKeyState(targetKey) & 0x8000) {
            sendPerfectJump();
            Sleep(jumpDelay); 
        } else {
            Sleep(10); 
        }
    }
}

extern "C" {
    __declspec(dllexport) void Start(int delay, int key) {
        if (threadRunning) return;
        targetKey = key;
        jumpDelay = (delay < 10) ? 10 : delay;
        threadRunning = true;
        _beginthread(BhopThread, 0, NULL);
    }

    __declspec(dllexport) void Stop() {
        threadRunning = false;
        // Финально «отжимаем» пробел на всякий случай
        INPUT input = {0};
        input.type = INPUT_KEYBOARD;
        input.ki.wScan = 0x39;
        input.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;
        SendInput(1, &input, sizeof(INPUT));
    }
}