import random
from tgbot.services.sqlite_logic import *
import time
CHARS = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890"

def create():
    promocode = ""
    check = True
    while check == True:
        time.sleep(1)
        for i in range(random.randint(15, 25)):
            promocode += random.choice(CHARS)
        check = check_promocode(promocode)
        if check == 0:
            check == False
    return promocode
