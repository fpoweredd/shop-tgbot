# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.services.api_sqlite import get_paymentx, get_userx
from tgbot.services.sqlite_logic import get_check_yoomoney, get_check_paymanual, get_url, get_check_payok
# Выбор способов пополнения
def refill_choice_finl():
    keyboard = InlineKeyboardMarkup()
    data_yoomoney = get_check_yoomoney()
    data_payok =  get_check_payok()
    data_paymanual = get_check_paymanual()
    get_payments = get_paymentx()
    active_kb = []


    if get_payments['way_form'] == "True":
        active_kb.append(InlineKeyboardButton("📋 QIWI форма", callback_data="refill_choice:Form"))
    if get_payments['way_number'] == "True":
        active_kb.append(InlineKeyboardButton("📞 QIWI номер", callback_data="refill_choice:Number"))
    if get_payments['way_nickname'] == "True":
        active_kb.append(InlineKeyboardButton("Ⓜ QIWI никнейм", callback_data="refill_choice:Nickname"))

    if len(active_kb) == 3:
        keyboard.add(active_kb[0], active_kb[1])
        keyboard.add(active_kb[2])
    elif len(active_kb) == 2:
        keyboard.add(active_kb[0], active_kb[1])
    elif len(active_kb) == 1:
        keyboard.add(active_kb[0])

    if data_yoomoney == 'True':
        keyboard.add(InlineKeyboardButton("ЮMoney 🌀", callback_data="refill_yoomoney"))

    if data_payok == 'True':
        keyboard.insert(InlineKeyboardButton("Картой / Криптовалютой 💳", callback_data="refill_payok"))

    if data_paymanual == 'True':
        keyboard.add(InlineKeyboardButton("Переводом 💵", callback_data="paymanual"))

    elif len(active_kb) >= 1:
        keyboard.add(InlineKeyboardButton("⬅ Вернуться ↩", callback_data="user_profile"))
    else:
        keyboard = None
    return keyboard


# Проверка киви платежа
def refill_bill_finl(send_requests, get_receipt, get_way):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🌀 Перейти к оплате", url=send_requests)
    ).add(
        InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"Pay:{get_way}:{get_receipt}")
    )

    return keyboard

def refill_bill_yoomoney(pay_amount, label, url_bill):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🌀 Перейти к оплате", url=url_bill)
    ).add(
        InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"Pay_yoomoney:{label}:{pay_amount}")
    )

    return keyboard

def refill_bill_payok(pay_amount, label, url_bill):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🌀 Перейти к оплате", url=url_bill)
    ).add(
        InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"Pay_payok:{label}:{pay_amount}")
    )

    return keyboard



# Кнопки при открытии самого товара
def products_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💰 Купить товар", callback_data=f"buy_item_open:{position_id}:{remover}")
    ).add(
        InlineKeyboardButton("♣️ Воспользоваться промокодом", callback_data=f"promocode_position_open:{position_id}:{category_id}:{remover}")
    ).add(
        InlineKeyboardButton("⬅ Вернуться ↩", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard

# Кнопка после воода промокода
def products_open_finl_after_promocod(position_id, category_id, remover, discount, promocode):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💰 Купить товар", callback_data=f"buy_item_open:{position_id}:{remover}:{discount}:{promocode}")
    ).add(
        InlineKeyboardButton("⬅ Вернуться ↩", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard

# Вернуться назад, промокоды
def promocode_back(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("⬅ Вернуться ↩", callback_data=f"buy_position_open:{position_id}:{category_id}:{remover}")
    )

    return keyboard



# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count, amount_pay, promocode):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"buy_item_confirm:yes:{position_id}:{get_count}:{amount_pay}:{promocode}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"buy_item_confirm:not:{position_id}:{get_count}:{amount_pay}:{promocode}")
    )

    return keyboard

#Предзаказ
def products_pre_order_select(position_id, remover, discount, promocode):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅", callback_data=f"buy_item_open_preorder:yes:{position_id}:{remover}:{discount}:{promocode}"),
        InlineKeyboardButton("❌", callback_data=f"buy_item_open_preorder:not:{position_id}:{remover}:{discount}:{promocode}")
    )

    return keyboard

def products_pre_order_confirm(position_id, get_count, price, promocode, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅", callback_data=f"pre_order_setup:yes:{position_id}:{get_count}:{price}:{promocode}:{remover}"),
        InlineKeyboardButton("❌", callback_data=f"pre_order_setup:not:{position_id}:{get_count}:{price}:{promocode}:{remover}")
    )

    return keyboard

def products_pre_order_finl(position_id, get_count, amount_pay, promocode):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅", callback_data=f"buy_item_confirm_pre_order:yes:{position_id}:{get_count}:{amount_pay}:{promocode}"),
        InlineKeyboardButton("❌", callback_data=f"buy_item_confirm_pre_order:not:{position_id}:{get_count}:{amount_pay}:{promocode}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl(user_name):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💌 Написать в поддержку", url=f"https://t.me/{user_name}"),
    )

    return keyboard


def replenish_user():
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("Пополнить баланс 💵", callback_data=f"user_refill")
    )
    return keyboard

def paymanual_support():
    user_id = get_url()
    if user_id == "None":
        keyboard = None
    else:
        get_user = get_userx(user_id=user_id)
        keyboard = InlineKeyboardMarkup(
        ).add(
            InlineKeyboardButton("Поддержка", url=f"https://t.me/{get_user['user_login']}")
        )
    return keyboard



def paymanual_finl(pay_amount, id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("Оплата совершена",  callback_data=f"paymanual_final:{pay_amount}:{id}")
    )
    return keyboard

def paymanual_admin_finl(pay_amount, username):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅",  callback_data=f"paymanual_admin:yes:{pay_amount}:{username}"),
        InlineKeyboardButton("❌",  callback_data=f"paymanual_admin:no:{pay_amount}:{username}")
    )
    return keyboard
