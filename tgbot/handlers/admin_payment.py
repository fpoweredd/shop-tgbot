# - *- coding: utf- 8 - *-
import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hlink

from tgbot.data.loader import dp, bot
from tgbot.keyboards.inline_admin import payment_choice_finl
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.yoomoney_api import get_token, url_for_token, check_yoomoney, get_balance
from tgbot.services.api_sqlite import update_paymentx, get_paymentx
from tgbot.services.sqlite_logic import update_pay_form, update_pay_form_paymanual, add_info_payok, get_data_payok, update_pay_form_payok

from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.keyboards.reply_all import payments_yoomoney,payments_paymanual, payments_payok
from tgbot.keyboards.inline_admin import add_payok
from tgbot.utils.const_functions import ded

from payok import payok_api

import asyncio, socket, urllib.request

###################################################################################
############################# ВЫБОР СПОСОБА ПОПОЛНЕНИЯ ############################
# Открытие способов пополнения
@dp.message_handler(IsAdmin(), text="🖲 Способы пополнений", state="*")
async def payment_systems(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🖲 Выберите способы пополнений</b>", reply_markup=payment_choice_finl())


# Включение/выключение самих способов пополнения
@dp.callback_query_handler(IsAdmin(), text_startswith="change_payment:")
async def payment_systems_edit(call: CallbackQuery):
    way_pay = call.data.split(":")[1]
    way_status = call.data.split(":")[2]

    get_payment = get_paymentx()

    if get_payment['qiwi_login'] != "None" and get_payment['qiwi_token'] != "None" or way_status == "False":
        if way_pay == "Form":
            if get_payment['qiwi_secret'] != "None" or way_status == "False":
                update_paymentx(way_form=way_status)
            else:
                await call.answer(
                    "❗ Приватный ключ отсутствует. Измените киви и добавьте приватный ключ для включения оплаты по Форме",
                    True)
                return
        elif way_pay == "Number":
            update_paymentx(way_number=way_status)
        elif way_pay == "Nickname":
            status, response = await (await QiwiAPI(call)).get_nickname()

            if status:
                update_paymentx(way_nickname=way_status, qiwi_nickname=response)
            else:
                await call.answer(response, True)
                return
    else:
        await call.answer("❗ Добавьте киви кошелёк перед включением Способов пополнений", True)
        return

    await call.message.edit_text("<b>🖲 Выберите способы пополнений</b>", reply_markup=payment_choice_finl())


###################################################################################
####################################### QIWI ######################################
# Изменение QIWI кошелька
@dp.message_handler(IsAdmin(), text="🥝 Изменить QIWI 🖍", state="*")
async def payment_qiwi_edit(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_qiwi_login")
    await message.answer("<b>🥝 Введите <code>номер (через +7, +380)</code> QIWI кошелька 🖍</b>")


# Проверка работоспособности QIWI
@dp.message_handler(IsAdmin(), text="🥝 Проверить QIWI ♻", state="*")
async def payment_qiwi_check(message: Message, state: FSMContext):
    await state.finish()

    await (await QiwiAPI(message, check_pass=True)).pre_checker()


# Баланс QIWI
@dp.message_handler(IsAdmin(), text="🥝 Баланс QIWI 👁", state="*")
async def payment_qiwi_balance(message: Message, state: FSMContext):
    await state.finish()

    await (await QiwiAPI(message)).get_balance()


######################################## ПРИНЯТИЕ QIWI ########################################
# Принятие логина для QIWI
@dp.message_handler(IsAdmin(), state="here_qiwi_login")
async def payment_qiwi_edit_login(message: Message, state: FSMContext):
    if message.text.startswith("+"):
        await state.update_data(here_qiwi_login=message.text)

        await state.set_state("here_qiwi_token")
        await message.answer(
            "<b>🥝 Введите <code>токен API</code> QIWI кошелька 🖍</b>\n"
            "❕ Получить можно тут 👉 <a href='https://qiwi.com/api'><b>Нажми на меня</b></a>\n"
            "❕ При получении токена, ставьте только первые 3 галочки.",
            disable_web_page_preview=True
        )
    else:
        await message.answer("<b>❌ Номер должен начинаться с + <code>(+7..., +380...)</code></b>\n"
                             "🥝 Введите <code>номер (через +7, +380)</code> QIWI кошелька 🖍")


# Принятие токена для QIWI
@dp.message_handler(IsAdmin(), state="here_qiwi_token")
async def payment_qiwi_edit_token(message: Message, state: FSMContext):
    await state.update_data(here_qiwi_token=message.text)

    await state.set_state("here_qiwi_secret")
    await message.answer(
        "<b>🥝 Введите <code>Приватный ключ 🖍</code></b>\n"
        "❕ Получить можно тут 👉 <a href='https://qiwi.com/p2p-admin/transfers/api'><b>Нажми на меня</b></a>\n"
        "❕ Вы можете пропустить добавление оплаты по Форме, отправив: <code>0</code>",
        disable_web_page_preview=True
    )


# Принятие приватного ключа для QIWI
@dp.message_handler(IsAdmin(), state="here_qiwi_secret")
async def payment_qiwi_edit_secret(message: Message, state: FSMContext):
    async with state.proxy() as data:
        qiwi_login = data['here_qiwi_login']
        qiwi_token = data['here_qiwi_token']

        if message.text == "0": qiwi_secret = "None"
        if message.text != "0": qiwi_secret = message.text

    await state.finish()

    cache_message = await message.answer("<b>🥝 Проверка введённых QIWI данных... 🔄</b>")
    await asyncio.sleep(0.5)

    await (await QiwiAPI(cache_message, qiwi_login, qiwi_token, qiwi_secret, True)).pre_checker()

###################################################################################
####################################### YooMoney ######################################

@dp.message_handler(IsAdmin(), text="🥝 Изменить Yoomoney", state="*")
async def payment_yoomoney_edit(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_yoomoney_login")
    await message.answer("<b>🥝 Введите <code>номер (через +7, +380)</code> YooMoney кошелька 🖍</b>")

######################################## ПРИНЯТИЕ YooMoney ########################################
# Принятие логина для Yoomoney
@dp.message_handler(IsAdmin(), state="here_yoomoney_login")
async def payment_yoomoney_edit_login(message: Message, state: FSMContext):
    if message.text.startswith("+"):
        invite_url = await bot.get_me()
        await state.update_data(here_yoomoney_login=message.text)
        await state.update_data(here_yoomoney_redirect_url= f"https://t.me/{invite_url.username}" )


        await state.set_state("here_yoomoney_client")
        await message.answer(
            "<b>💵 Введите <code>cliend ID</code> Yoomoney кошелька</b>\n"
            "❕ Получить можно тут 👉 <a href='https://yoomoney.ru/myservices/new'><b>Нажми на меня</b></a>\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            f"🔗 При регистрации приложения, в качестве ссылок ставьте это  👉 <code>https://t.me/{invite_url.username}</code>",
            disable_web_page_preview=True

        )
    else:
        await message.answer("<b>❌ Номер должен начинаться с + <code>(+7..., +380...)</code></b>\n"
                             "🥝 Введите <code>номер (через +7, +380)</code> YooMoney кошелька 🖍")

# Принятие токена для Yoomoney
@dp.message_handler(IsAdmin(), state="here_yoomoney_client")
async def payment_yoomoney_edit_token(message: Message, state: FSMContext):
    invite_url = await bot.get_me()
    urlToken = url_for_token(message.text, f"https://t.me/{invite_url.username}" )
    if urlToken == False:
        await message.answer("Возникла ошибка с подключением к серверу. Попробуйте чуть позже ❌")
    else:
        await state.update_data(here_yoomoney_client_id=message.text)
        await state.set_state("here_yoomoney_token")
        await message.answer(
            "<b>Перейдите по ссылке и подтверждаете приложение\n"
            "Затем пришлите ссылку, которую вы получили в поисковой строке</b>\n"
            f"❕ Ссылка тут 👉 <a href='{urlToken}'><b>Нажми на меня</b></a>\n"
            "❕ Если у вас возникла проблема, вы можете начать этап добавления заново",
            disable_web_page_preview=True)


@dp.message_handler(IsAdmin(), state="here_yoomoney_token")
async def payment_yoomoney_get_token(message: Message, state: FSMContext):
    async with state.proxy() as data:
        client_id = data['here_yoomoney_client_id']
        redirect_url = data['here_yoomoney_redirect_url']

    token = get_token(message.text, client_id, redirect_url)
    #Обработка ошибокegfk
    if token == "Empty token":
        await message.answer("<b>Нам не удалось получить токен. 😥\nПовторите попытку!</b>")
    elif token == "invalid_request":
        await message.answer("<b>Возникла ошибка при подключение к серверу. 😥\n""Повторите попытку!</b>")
    elif token == "unauthorized_client":
        await message.answer("<b>Неправильно введен <code>client_id</code> 😥\n""Повторите попытку!</b>")
    else:
        await message.answer(f"<b>💵 Проверка введённых Yooumoney данных... 🔄</b>")
        message_text = check_yoomoney(token, client_id)
        await asyncio.sleep(2)
        await message.answer(message_text)
        await state.finish()

@dp.message_handler(IsAdmin(), text="🥝 Проверить Yoomoney", state="*")
async def payment_yoomoney_edit(message: Message, state: FSMContext):
    message_text = check_yoomoney(None, None)
    await message.answer(message_text)

@dp.message_handler(IsAdmin(), text="🥝 Баланс YooMoney 👁", state="*")
async def payment_yoomoney_edit(message: Message, state: FSMContext):
    message_text = get_balance()
    await message.answer(message_text)


@dp.message_handler(IsAdmin(), text = ['✅ Включить Yoomoney', '❌ Выключить Yoomoney'], state="*")
async def payment_yoomoney_off_on(message: Message, state: FSMContext):
    if message.text == '✅ Включить Yoomoney':
        update_pay_form('True')
    else:
        update_pay_form('False')
    await message.answer("Успешно 👍", reply_markup = payments_yoomoney())

#paymanual

@dp.message_handler(IsAdmin(), text="💵 Переводом 💵", state="*")
async def payment_paymanual_edit(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>Включить или выключить способ оплаты по переводу?🖍</b>", reply_markup=payments_paymanual())


@dp.message_handler(IsAdmin(), text = ['✅ Включить', '❌ Выключить'], state = '*')
async def payment_paymanual_final(message: Message, state: FSMContext):
    if message.text == '✅ Включить':
        update_pay_form_paymanual('True')
    else:
        update_pay_form_paymanual('False')
    await message.answer("Успешно 👍", reply_markup=payments_paymanual())

#####################################################
####################PAYOK############################

####################ДОБАВЛЕНИЕ #######################
@dp.message_handler(IsAdmin(), text="🟠 Изменить Payok", state="*")
async def payok_edit(message: Message, state: FSMContext):
    await state.finish()


    await state.set_state("here_payok_api_key")
    await message.answer("<b>🟠 Напиши сюда <code>API ключ</code> 🖍</b>")

@dp.message_handler(IsAdmin(), state="here_payok_api_key")
async def here_payok_api_key(message: Message, state: FSMContext):

    await state.update_data(api_key_payok = message.text)
    await state.set_state("here_payok_api_id")
    await message.answer("Прекрасно!\n\n<b>🟠 Напиши сюда <code>API ID</code> 🖍</b>")


@dp.message_handler(IsAdmin(), state="here_payok_api_id")
async def here_payok_api_id(message: Message, state: FSMContext):
    await state.update_data(api_id_payok = message.text)
    bot_info = await bot.get_me()
    invite_url = f"https://t.me/{bot_info.username}"
    await state.set_state("here_payok_secret_key")
    await message.answer(f"<i>Теперь создайте магазин, в качестве URL магазина поставьте ссылку на бота ➡️ <code>{invite_url}</code></i>!\n\n<b>🟠 И напиши сюда <code>Secret Key</code> в настройке магазина 🖍</b>")

@dp.message_handler(IsAdmin(), state="here_payok_secret_key")
async def here_payok_secret_key(message: Message, state: FSMContext):
    await state.update_data(secret_key_payok = message.text)
    bot_info = await bot.get_me()
    invite_url = f"https://t.me/{bot_info.username}"
    await state.set_state("here_payok_api")
    await message.answer(f"<b>🟠 Прекрасно! Введи  сюда <code>ID магазина</code> в настройке магазина 🖍</b>")

    @dp.message_handler(IsAdmin(), state="here_payok_api")
    async def here_payok_secret_key(message: Message, state: FSMContext):
        await state.update_data(shop_id_payok=message.text)
        await state.set_state("paypk_finish")
        ip_adress = str(urllib.request.urlopen('https://ident.me').read().decode('utf8'))

        await message.answer(f"<b>🟠 Последний шаг, добавьте этот айпи <code>{ip_adress}</code> в список разрешенных IP 🖍</b>", reply_markup=add_payok())


@dp.callback_query_handler(IsAdmin(), text="add_payok", state="paypk_finish")
async def payok_finish(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        api_key = data['api_key_payok']
        api_id = data['api_id_payok']
        secret_key = data['secret_key_payok']
        shop_id = data['shop_id_payok']

    await call.message.answer(f"<b>🟠 Отлично! Идет проверка доступа к магазину</b>")
    await asyncio.sleep(1)
    await call.message.delete()


    try:
        info = payok_api.getBalance(api_id, api_key)
        add_info_payok(api_key, api_id, secret_key, shop_id)
        await call.message.answer(ded(f"""
        <b>PAYOK успешно подключен!</b>
        
        Ваш баланс составляет <code>{info['balance']}₽</code>"""), reply_markup=payments_payok())
    except Exception as i:
        print(i)
        await call.message.answer("<b>Возникла ошибка! Проверьте введенные вами данные и повторите попытку</b>")


@dp.message_handler(IsAdmin(), text="🟠 Проверить Payok", state="*")
async def check_payok(message: Message, state: FSMContext):
    info_payok = get_data_payok()
    balance = payok_api.getBalance(info_payok[1], info_payok[0])

    balance = balance['balance']
    await message.answer(ded(f"""
    <code>PAYOK ПОДКЛЮЧЕН ✅</code>\n
    <b>API_ID: <code>{info_payok[1]}</code>
    SECRET_KEY: <code>{info_payok[2]}</code>
    SHOP_ID: <code>{info_payok[3]}</code>
    Баланс: <code>{balance}</code>
    Статус: <code>Подключен✅</code></b>"""))

@dp.message_handler(IsAdmin(), text="🟠 Баланс Payok 👁", state="*")
async def balance_payok(message: Message, state: FSMContext):
    info_payok = get_data_payok()
    balance = payok_api.getBalance(info_payok[1], info_payok[0])

    balance = balance['balance']
    await message.answer(f"Баланс: <code>{balance}</code>")


@dp.message_handler(IsAdmin(), text = ['✅ Включить Payok', '❌ Выключить Payok'], state="*")
async def payment_payok_off_on(message: Message, state: FSMContext):
    if message.text == '✅ Включить Payok':
        update_pay_form_payok('True')
    else:
        update_pay_form_payok('False')
    await message.answer("Успешно 👍", reply_markup = payments_payok())
