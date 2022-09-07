import getpass
import logging
import sys
sys.path.insert(0, 'LSR')
sys.path.insert(0, 'DVR')
sys.path.insert(0, 'Flooding')
from lsr import mainlsr
from dvr import maindvr
from fl import mainfl

debugging = False

if __name__ == '__main__':
     # Debbuging mode, if it is True, all functions will be debugged correctly
    if debugging:

        useLogin = logging.getLogger()
        useLogin.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        setting_logger_formatlogs = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        console_handler.setFormatter(setting_logger_formatlogs)
        useLogin.addHandler(console_handler)

    # Main menu cycle of the program
    mainMenu = 0
    # while mainMenu != 4:
        # try:
    mainMenu = int(input("""

Choose the number of the option you want to do:
1. FLOODING 
2. DVR
3. LSR
4. Exit

>"""))
    
    if(mainMenu == 1):
        print("FLOODING")
        mainfl()
    elif(mainMenu == 2):
        print("DISTANCE VECTOR ROUTING")
        maindvr()
    elif(mainMenu == 3):
        print("LINK STATE ROUTING")
        mainlsr()
    elif(mainMenu == 4):
        # Exit the program
        print("You are always welcome !")
    else:
        print("Choose a valid option")
        # except: 
        #     print("Choose a valid option")