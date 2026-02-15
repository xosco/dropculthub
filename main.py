import webview
import os
import sys
import requests
import ctypes
import time
import webbrowser
from datetime import datetime

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Api:
    def __init__(self):
        self._window = None
        self.clicker_dll = None
        self.jump_dll = None
        self.logs = []
        self.logging_enabled = True

    def set_window(self, window):
        self._window = window

    def add_log(self, category, action, status="Инфо"):
        if not self.logging_enabled: return
        now = datetime.now().strftime("%H:%M:%S")
        self.logs.append({"time": now, "category": category, "action": action, "status": status})

    def minimize_window(self): self._window.minimize()
    def close_window(self): 
        try:
            if self.clicker_dll: self.clicker_dll.Stop()
            if self.jump_dll: self.jump_dll.Stop()
        except: pass
        self._window.destroy()
        os._exit(0)
    def toggle_fullscreen(self): self._window.toggle_fullscreen()

    def launch_roblox(self):
        webbrowser.open("https://www.roblox.com/home")
        self.add_log("System", "Запуск Roblox", "Успех")
        self._window.evaluate_js("showNotify('Roblox открыт', 'success')")

    def launch_clicker(self, cps, key_code_str):
        path = resource_path("clicker.dll")
        if not os.path.exists(path): return
        try:
            cps_val = int(cps)
            key_code = int(key_code_str, 16)
            if not self.clicker_dll: self.clicker_dll = ctypes.WinDLL(os.path.abspath(path))
            self.clicker_dll.Start.argtypes = [ctypes.c_int, ctypes.c_int]
            self.clicker_dll.Stop()
            time.sleep(0.1)
            self.clicker_dll.Start(cps_val, key_code)
            self._window.evaluate_js("showNotify('Кликер активен','success')")
            self.add_log("Clicker", "Запуск", "OK")
        except: self._window.evaluate_js("showNotify('Ошибка Clicker DLL','error')")

    def stop_clicker(self):
        if self.clicker_dll: self.clicker_dll.Stop()

    def launch_jump(self, key_code_str):
        path = resource_path("jump.dll")
        if not os.path.exists(path):
            self._window.evaluate_js("showNotify('jump.dll не найден!','error')")
            return
        try:
            key_code = int(key_code_str, 16)
            if not self.jump_dll: 
                self.jump_dll = ctypes.WinDLL(os.path.abspath(path))
            self.jump_dll.Start.argtypes = [ctypes.c_int, ctypes.c_int]
            self.jump_dll.Stop.argtypes = []
            self.jump_dll.Stop()
            time.sleep(0.1)
            # Передаем 20мс задержки и выбранную клавишу
            self.jump_dll.Start(20, key_code)
            self._window.evaluate_js("showNotify('Jump Macro готов: Удерживайте клавишу','success')")
            self.add_log("Jump", "Система активна (Hold)", "OK")
        except Exception as e:
            self._window.evaluate_js("showNotify('Ошибка Jump DLL','error')")

    def stop_jump(self):
        if self.jump_dll:
            try:
                self.jump_dll.Stop()
                self._window.evaluate_js("showNotify('Jump Macro выключен','info')")
                self.add_log("Jump", "Остановлен", "OK")
            except: pass

    def get_logs(self): return self.logs
    def set_logging_state(self, state): self.logging_enabled = state
    def log_theme_change(self, theme): self.add_log("GUI", f"Тема: {theme}", "Успех")

    def init_launcher(self):
        user_id = '8135080197' 
        profile_data = {"success": False}
        try:
            u_res = requests.get(f"https://users.roblox.com/v1/users/{user_id}", timeout=5).json()
            t_res = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png", timeout=5).json()
            profile_data = {
                "success": True, "username": u_res.get("name"), "displayName": u_res.get("displayName"), "avatarUrl": t_res["data"][0]["imageUrl"]
            }
            self.add_log("Cloud", "Профиль загружен", "Успех")
        except: pass
        return {"profile": profile_data}

api = Api()
html_path = resource_path("index.html")
window = webview.create_window("Misty Launcher", html_path, width=1150, height=750, frameless=True, js_api=api)
api.set_window(window)
webview.start()