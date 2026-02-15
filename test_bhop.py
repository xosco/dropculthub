import ctypes
import os
import sys
import platform
import time

def diagnose_dll():
    print("=== ДИАГНОСТИКА СИСТЕМЫ ===")
    print(f"Версия Python: {sys.version}")
    print(f"Архитектура: {platform.architecture()[0]}")
    print(f"Рабочая директория: {os.getcwd()}")
    
    dll_name = "jump.dll"
    dll_path = os.path.abspath(dll_name)
    print(f"Ищем файл по пути: {dll_path}")

    if not os.path.exists(dll_path):
        print("❌ ОШИБКА: Файл jump.dll не найден в папке со скриптом!")
        return False

    print("✅ Файл найден. Пробуем загрузить...")

    try:
        # Пытаемся загрузить библиотеку
        # Используем WinDLL для stdcall (Windows API)
        lib = ctypes.WinDLL(dll_path)
        print("✅ DLL успешно загружена в память!")
        
        # Проверяем наличие функции Ping
        if hasattr(lib, 'Ping'):
            res = lib.Ping()
            print(f"✅ Тестовая функция вызвана! Ответ: {res}")
            return lib
        else:
            print("❌ ОШИБКА: Функция 'Ping' не найдена. Возможно, имена функций 'искажены' (mangled).")
            return False

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА ЗАГРУЗКИ: {e}")
        # Дополнительная проверка на разрядность
        if "is not a valid Win32 application" in str(e):
            print("   СОВЕТ: Скорее всего, вы собрали 64-битную DLL, а Python у вас 32-битный (или наоборот).")
        return False

if __name__ == "__main__":
    bhop_lib = diagnose_dll()
    
    if bhop_lib:
        print("\n--- ЗАПУСК БХОПА ---")
        print("Нажми SPACE для включения/выключения.")
        print("Нажми END для выхода.")
        try:
            # Задержка 25 мс
            bhop_lib.RunBhop(25)
        except KeyboardInterrupt:
            print("\nСкрипт остановлен пользователем.")
    else:
        print("\nЗапуск невозможен. Исправьте ошибки выше.")
        input("Нажмите Enter, чтобы выйти...")