from time import sleep
from TokenInsert import on_login
import time
import pyautogui
from pyzbar.pyzbar import decode
from PIL import Image
import sqlite3

import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Перезапуск с правами админа
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()


line_num = 0

# Подключение к базе (создаст файл, если нет)
conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT,
    state TEXT
    )
''')


# Функция для добавления строки с QR-текстом
def add_data(token, state):
    global cursor
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO data (token, state) 
        VALUES (?, ?)
    ''', (token, state))
    conn.commit()

#return T-F
def qr_check():
    screenshot = pyautogui.screenshot()
    screenshot.save('screen.png')
    img = Image.open('screen.png')
    qrs = decode(img)
    if qrs:
        print("Найдены QR-коды:", [qr.data.decode() for qr in qrs])
        return True
    else:
        print("QR-коды не найдены")  # Проверка наличия QR [web:22]
        return False

#return T-F
import win32gui
import win32process
import psutil


# Коллбэк на верхнем уровне - ИЗБАВИТ от ошибки!
def enum_windows_callback(hwnd, ctx):
    pid, proc_name, found_flag = ctx
    try:
        if win32gui.IsWindowVisible(hwnd):
            _, pid_window = win32process.GetWindowThreadProcessId(hwnd)
            if pid_window == pid:
                title = win32gui.GetWindowText(hwnd)
                if title == 'Steam' and proc_name == 'steamwebhelper.exe':
                    print(f"Найден Steam! PID {pid}")
                    found_flag[0] = True  # Изменяем список (mutable)
                    return False
    except Exception:
        pass
    return True


def get_steam_result():
    found_flag = [False]  # Список для передачи состояния

    for proc in psutil.process_iter(['pid', 'name']):
        pid = proc.info['pid']
        proc_name = proc.info['name']

        try:
            # Передаем данные через ctx
            ctx = (pid, proc_name, found_flag)
            win32gui.EnumWindows(enum_windows_callback, ctx)

            if found_flag[0]:
                return True
        except Exception as e:
            print(f"Ошибка процесса {pid}: {e}")
            continue

    return False




def check_with_timeout(check_func, timeout=15):
    for i in range(timeout):
        if check_func():  # Замените на вашу функцию проверки
            print(f'check success in {i}s')
            return "valid"
        time.sleep(1)
        print(f'check failed with timeout {i}')
    if qr_check():
        return "need review"
    else:
        return "invalid"

with open('input.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines()]

for line in lines:  # ← line = текущая строка из файла
    line_num += 1
    on_login(line)
    sleep(10)
    result=check_with_timeout(get_steam_result)
    if result=='valid':
        print(f'{line} valid')
        add_data(line, 'valid')
    elif result=='need review':
        print(f'{line} need review')
        add_data(line, 'need review')
    else:
        add_data(line, 'RES')
        print(f'{line} RES')
