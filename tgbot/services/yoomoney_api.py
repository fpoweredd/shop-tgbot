from typing import List
import requests
from async_class import AsyncClass
from yoomoney import Client
from tgbot.utils.const_functions import ded
from yoomoney import Quickpay
from tgbot.services import sqlite_logic
import random, time


SCOPE = ["account-info","operation-history","operation-details", "incoming-transfers", "payment-p2p", "payment-shop", ]
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


def url_for_token(client_id, redirect_uri):
    url = "https://yoomoney.ru/oauth/authorize?client_id={client_id}&response_type=code" \
          "&redirect_uri={redirect_uri}&scope={scope}".format(client_id=client_id, redirect_uri=redirect_uri,  scope='%20'.join([str(elem) for elem in SCOPE]), )
#TODO написать исключения
    response = requests.request("POST", url, headers=HEADERS)
    if response.status_code == 200:
        return response.url
    else:
        return False

def get_token(url, client_id, redirect_uri):
    code = str(url)
    try:
        code = code[code.index("code=") + 5:].replace(" ","")
    except:
        pass
    url = "https://yoomoney.ru/oauth/token?code={code}&client_id={client_id}&" \
          "grant_type=authorization_code&redirect_uri={redirect_uri}".format(code=str(code), client_id=client_id, redirect_uri=redirect_uri,   )
    response = requests.request("POST", url, headers=HEADERS)
    if "error" in response.json():
        return  response.json()["error"]
    if response.json()['access_token'] == "":
        return "Empty token"

    return response.json()['access_token']


def check_yoomoney(token, client_id):
    if token == None:
        try:
            token = sqlite_logic.get_yoomoney()[0]
            client_id = sqlite_logic.get_yoomoney()[1]
        except TypeError:
            pass
    try:
        client = Client(token)
        try:
            user = client.account_info()
        except requests.exceptions.ConnectTimeout:
            message_text = ded(f"""
                    <b>Превышено время ожидания! Повторите попытку</b>
                    """)
            return message_text
        sqlite_logic.add_info_yoomoney(client_id, token, user.account)
        message_text = ded(f"""
        <code>YOOMONEY ПОДКЛЮЧЕН ✅</code>\n
        <b>Номер аккаунта: <code>{user.account}</code>
        Баланс: <code>{user.balance}</code>
        Статус: <code>{user.account_status}</code>
        Тип: <code>{user.account_type}</code></b>
        """)
    except AttributeError:
        message_text = ded(f"""<b>Ошибка!</b>
        Yoomoney не подключен к боту
        Подключите при помощи кнопки <code>"Изменить yoomoney"</code>
        """)

    return message_text


def get_balance():
    token = sqlite_logic.get_yoomoney()[0]
    client_id = sqlite_logic.get_yoomoney()[1]
    try:
        client = Client(token)
        user = client.account_info()
        sqlite_logic.add_info_yoomoney(client_id, token, user.account)
        message_text = ded(f"""
        Баланс: <code>{user.balance}</code>
        """)
    except AttributeError:
        message_text = ded(f"""<b>Ошибка!</b>
        Yoomoney не подключен к боту
        Подключите при помощи кнопки <code>"Изменить yoomoney"</code>
        """)

    return message_text


def generate_payment(pay_amount, label_):
    number = sqlite_logic.get_yoomoney()[2]
    try:
        quickpay = Quickpay(
                    receiver=str(number),
                    quickpay_form="shop",
                    targets=str(random.randint(999, 10000)),
                    paymentType="SB",
                    sum=pay_amount,
                    label= label_
                    )
        return quickpay.redirected_url
    except requests.exceptions.ConnectTimeout:
        print(quickpay)
        print('Тут')

def check_payment(label):
    token = sqlite_logic.get_yoomoney()[0]
    client_id = sqlite_logic.get_yoomoney()[1]

    client = Client(token)
    history = client.operation_history(label=str(label))
    if history.operations == []:
        return False
    else:
        for operation in history.operations:
            if operation.status == 'success':
                return True

def get_receipt():
    bill_receipt = str(int(time.time() * 100))
    return bill_receipt