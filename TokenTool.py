import colorama
from colorama import Fore
from TokenInsert import *

def init():
    user_input= input(Fore.GREEN + "Input:" + Fore.CYAN)
    inp=str(user_input)
    if inp.lower() == "r" or inp.lower() == "reset":
        reset_steam()
    else:
        on_login(user_input)
    init()

print(Fore.GREEN + 'Select the desired option:\ntype "r" or "reset" to reset the main service. \nInsert the authorization token to log in to your account.\n'+ Fore.YELLOW +"buy tokens - skittens.mysellauth.com")
init()