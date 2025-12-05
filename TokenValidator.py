from time import sleep
from TokenInsert import on_login
import time
import pyautogui
from pyzbar.pyzbar import decode
from PIL import Image
import sqlite3
import win32gui
import win32process
import psutil


conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT,
    state TEXT
    )
''')


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

#callback uses in get_steam_result()
def enum_windows_steam_callback(hwnd, ctx):
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

#find process with name 'steam', we need this to understand what token is REALLY valid
def get_steam_result():
    found_flag = [False]

    for proc in psutil.process_iter(['pid', 'name']):
        pid = proc.info['pid']
        proc_name = proc.info['name']

        try:
            # Передаем данные через ctx
            ctx = (pid, proc_name, found_flag)
            win32gui.EnumWindows(enum_windows_steam_callback, ctx)

            if found_flag[0]:
                return True
        except Exception as e:
            print(f"Ошибка процесса {pid}: {e}")
            continue
    return False

#not instant func to check token valid
def check_with_timeout(check_func, timeout=15):
    for i in range(timeout):
        if check_func():
            print(f'check success in {i}s')
            return "valid"
        time.sleep(1)
        print(f'check failed with timeout {i}')
    if qr_check():
        return "need review"
    else:
        return "invalid"

#open input.txt file to get lines with tokens
with open('input.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines()]

#check input txt
if lines:
    # loop all lines
    line_num = 0
    for line in lines:  # ← line = current line in file
        line_num += 1
        on_login(line)
        sleep(10)
        result = check_with_timeout(get_steam_result)
        if result == 'valid':
            print(f'{line} valid')
            add_data(line, 'valid')
        elif result == 'need review':
            print(f'{line} need review')
            add_data(line, 'need review')
        else:
            add_data(line, 'RES')
            print(f'{line} RES')
else:
    print('Error : input.txt are empty')
