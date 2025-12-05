import stat
import zlib
import base64
import json
import random
import string
import psutil
import subprocess
import shutil
import winreg
import os
import time
import win32crypt
import vdf
from jwt_helper import verify_steam_jwt


# a set of features that I shamelessly stole ( sorry orig authors shame on me )

def get_steam_install_path():
    steam_pid = get_pid('steam.exe')
    if steam_pid != 0:
        process = psutil.Process(steam_pid)
        steam_path = process.exe()
        subprocess.run('taskkill /f /im steam.exe', shell=True)
        subprocess.run('taskkill /f /im steamwebhelper.exe', shell=True)
        time.sleep(2)
    else:
        steam_path = read_registry_value('Software\\Classes\\steam\\Shell\\Open\\Command', '').replace('"', '')
        steam_path = steam_path[:len(steam_path) - 6]
    return steam_path[:len(steam_path) - 9]

def get_local_vdf_path():
    app_data_path = os.getenv('localappdata')
    if app_data_path is None:
        print("Failed to get localappdata environment variable.")
    return os.path.join(app_data_path, 'Steam', 'local.vdf')

def steam_decrypt(encrypted_hex_data):
    encrypted_data = bytes.fromhex(encrypted_hex_data)
    decrypted_data = win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)
    return decrypted_data[1].decode('utf-8')

def remove_readonly(func, path, excinfo):
    if os.path.exists(path):
        try:
            os.chmod(path, stat.S_IWRITE)
        except Exception:
            pass
        func(path)

def steam_encrypt(token, account_name):
    data_to_encrypt = token.encode('utf-8')
    byte_string = b'B\x00O\x00b\x00f\x00u\x00s\x00c\x00a\x00t\x00e\x00B\x00u\x00f\x00f\x00e\x00r\x00\x00\x00'
    encrypted_data = win32crypt.CryptProtectData(data_to_encrypt, byte_string.decode('utf-8'), account_name.encode('utf-8'), None, None, 17)
    return encrypted_data.hex()

def read_registry_value(key_path, value_name):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(key, value_name)
    winreg.CloseKey(key)
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    return value

def get_pid(process_name):
    for process in psutil.process_iter():
        if process.name() == process_name:
            return process.pid
    return 0

def compute_crc32(data):
    crc32_value = zlib.crc32(data.encode('utf-8'))
    return f'{crc32_value:08x}'.lstrip('0')

def parse_eya(eya):
    token_arr = eya.split('.')
    if len(token_arr) != 3:
        print("Error:Invalid token!")
        return None
    padding = len(token_arr[1]) % 4
    if padding != 0:
        token_arr[1] += '=' * (4 - padding)
    return base64.b64decode(token_arr[1]).decode('utf-8')

def build_config(mtbf, steam_id, account_name):
    config = {
        "InstallConfigStore": {
            "Software": {
                "Valve": {
                    "Steam": {
                        "AutoUpdateWindowEnabled": "0",
                        "ipv6check_http_state": "bad",
                        "ipv6check_udp_state": "bad",
                        "ShaderCacheManager": {
                            "HasCurrentBucket": "1",
                            "CurrentBucketGPU": "b4799b250d4196b0;36174e7cc31a08f9",
                            "CurrentBucketDriver": "W2:c18b09d9c69329b41cdbbf3de627bc9f;W2:ee32edf67d134b7cc2ec0cdecbd00037"
                        },
                        "RecentWebSocket443Failures": "",
                        "RecentWebSocketNon443Failures": "",
                        "RecentUDPFailures": "",
                        "RecentTCPFailures": "",
                        "Accounts": {
                            account_name: {
                                "SteamID": steam_id
                            }
                        },
                        "CellIDServerOverride": "170",
                        "MTBF": mtbf,
                        "cip": "02000000507a6c24d6e96c6b00004021a356",
                        "SurveyDate": "2017-10-22",
                        "SurveyDateVersion": "-1724767764117155760",
                        "SurveyDateType": "3",
                        "Rate": "30000"
                    }
                }
            },
            "SDL_GamepadBind": {
                "03000000de280000ff11000001000000,Steam Virtual Gamepad": "a:b0,b:b1,back:b6,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,leftshoulder:b4,leftstick:b8,lefttrigger:+a2,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b9,righttrigger:-a2,rightx:a3,righty:a4,start:b7,x:b2,y:b3,platform:Windows",
                "03000000de280000ff11000000000000,Steam Virtual Gamepad": "a:b0,b:b1,back:b6,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,leftshoulder:b4,leftstick:b8,lefttrigger:+a2,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b9,righttrigger:-a2,rightx:a3,righty:a4,start:b7,x:b2,y:b3",
                "03000000de280000ff11000000007701,Steam Virtual Gamepad": "a:b0,b:b1,x:b2,y:b3,back:b6,start:b7,leftstick:b8,rightstick:b9,leftshoulder:b4,rightshoulder:b5,dpup:b10,dpdown:b12,dpleft:b13,dpright:b11,leftx:a1,lefty:a0~,rightx:a3,righty:a2~,lefttrigger:a4,righttrigger:a5,"
            },
            "streaming": {
                "ClientID": "-6167702798309564492"
            },
            "Music": {
                "LocalLibrary": {
                    "Directories": {
                        "0": "0200000013500d50b7e96d1b621bcb56f5a12ce5e0651b4c3b3a50a59063d16c7d6fc334d903be2347030590f9d63c5a09370ac77bcfc6c945d0b348b91a586438e4162d56e494c9c73173ae",
                        "1": "0200000013500d50b7e96d1b621bcb56f2a12ce3e76508523b7812f4c237ec51786ff63aac72a1212b7416a2f0d71b7039302dcc2ebca3bb45d2c02bd87645623d8a784832e49cc1a01779a2209be04c"
                    }
                }
            }
        }
    }
    return vdf.dumps(config)

def build_login_users(steam_id, account_name):
    login_users = {
        "users": {
            steam_id: {
                "AccountName": account_name,
                "PersonaName": account_name,
                "RememberPassword": "1",
                "WantsOfflineMode": "0",
                "SkipOfflineModeWarning": "0",
                "AllowAutoLogin": "1",
                "MostRecent": "1",
                "Timestamp": str(int(time.time()))
            }
        }
    }
    return vdf.dumps(login_users)

def build_local(crc32, jwt):
    local = {
        "MachineUserConfigStore": {
            "Software": {
                "Valve": {
                    "Steam": {
                        "ConnectCache": {
                            crc32: jwt
                        }
                    }
                }
            }
        }
    }
    return vdf.dumps(local)

def reset_steam():
    path = get_steam_install_path()
    for directory in [os.path.join(path, 'userdata'), os.path.join(path, 'config')]:
        if os.path.exists(directory):
            shutil.rmtree(directory, onerror=remove_readonly)
    local_vdf_path = get_local_vdf_path()
    if os.path.exists(local_vdf_path):
        os.remove(local_vdf_path)
    subprocess.Popen(os.path.join(path, 'steam.exe'), shell=True)
    print("Reset Completed:Steam has been reset successfully.")

def login_game(eya, account_name):
    if '@' in account_name:
        # Remove everything after @
        account_name = account_name.split('@')[0]
    crc32_account_name = compute_crc32(account_name) + "1"
    json_data = json.loads(parse_eya(eya))
    if not json_data:
        return
    steam_id = json_data['sub']
    mtbf = ''.join(random.choices(string.digits, k=9))
    jwt = steam_encrypt(eya, account_name)
    path = get_steam_install_path()
    local_vdf_path = get_local_vdf_path()
    if os.path.exists(local_vdf_path):
        os.remove(local_vdf_path)
    try:
        os.makedirs(os.path.join(path, 'config'))
    except FileExistsError:
        pass
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Valve\\Steam', 0, winreg.KEY_WRITE)
    winreg.SetValueEx(key, 'AutoLoginUser', 0, winreg.REG_SZ, account_name)
    winreg.CloseKey(key)
    config = build_config(mtbf, steam_id, account_name)
    login_users = build_login_users(steam_id, account_name)
    local = build_local(crc32_account_name, jwt)
    remove_readonly(os.remove, os.path.join(path, 'config', 'config.vdf'), None)
    with open(os.path.join(path, 'config', 'config.vdf'), 'w', encoding='utf-8') as f:
        f.write(config)
    remove_readonly(os.remove, os.path.join(path, 'config', 'loginusers.vdf'), None)
    with open(os.path.join(path, 'config', 'loginusers.vdf'), 'w', encoding='utf-8') as f:
        f.write(login_users)
    local_vdf_path = get_local_vdf_path()
    if os.path.exists(local_vdf_path):
        remove_readonly(os.remove, local_vdf_path, None)
        os.remove(local_vdf_path)
    with open(local_vdf_path, 'w', encoding='utf-8') as f:
        f.write(local)
    subprocess.Popen(os.path.join(path, 'steam.exe'), shell=True)
    print( "Login attempt. " +  "If you are redirected to the account selection page, the token has expired. If the login window appears, enter the token again. ")

def on_login(user_input):
    user_input = user_input.replace('EyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0', 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0')
    user_input = user_input.replace(' ', '').replace('\n', '').replace('\r', '')
    text = user_input.split('----')
    if len(text) < 2:
        print("Error:Invalid input format. You should include the account name and eyA token separated by '----'.")
        return
    eya = ""
    account_name = ""
    for part in text:
        if 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.' in part:
            eya = part
            account_name = text[0].lower()
            break
    if eya != "":
        expire_time = verify_steam_jwt(eya)
        if expire_time is False:
            print( "Error:Invalid token. Please confirm you have entered the correct account key.")
        elif expire_time < 0:
            print("Error:eyA token has expired.")
        else:
            login_game(eya, account_name)
            days = expire_time // 86400
            hours = (expire_time % 86400) // 3600
            minutes = (expire_time % 3600) // 60
            #seconds = expire_time % 60 - secnds are useless
            print(f"Token is valid for {days}d, {hours}h, {minutes}m")
    else:
        print("Error:Invalid input format.")

