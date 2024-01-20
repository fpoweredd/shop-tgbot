# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.data.loader import dp
from tgbot.keyboards.inline_user import refill_bill_finl, refill_choice_finl, refill_bill_yoomoney, paymanual_support, paymanual_finl, paymanual_admin_finl, refill_bill_payok
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_sqlite import update_userx, get_refillx, add_refillx, get_userx
from tgbot.services.sqlite_logic import get_data_payok
from tgbot.services.json_logic import get_texts
from tgbot.utils.const_functions import get_date, get_unix
from tgbot.utils.misc_functions import send_admins
from tgbot.services.yoomoney_api import generate_payment, check_payment, get_receipt
from tgbot.utils.const_functions import ded
from tgbot.data.loader import bot


from payok import payok_api
import random


min_input_qiwi = 10  # Минимальная сумма пополнения в рублях


# Выбор способа пополнения
@dp.callback_query_handler(text="user_refill", state="*")
async def refill_way(call: CallbackQuery, state: FSMContext):
    get_kb = refill_choice_finl()

    if get_kb is not None:
        await call.message.edit_text("<b>💰 Выберите способ пополнения</b>", reply_markup=get_kb)
    else:
        await call.answer("⛔ Пополнение временно недоступно", True)

# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="refill_choice", state="*")
async def refill_way_choice(call: CallbackQuery, state: FSMContext):
    get_way = call.data.split(":")[1]

    await state.update_data(here_pay_way=get_way)
    await state.set_state("here_pay_amount")
    await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")

@dp.callback_query_handler(text_startswith="refill_yoomoney", state="*")
async def refill_way_yoomoney(call: CallbackQuery, state: FSMContext):
    await state.set_state("here_pay_amount_yoomoney")
    await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")

@dp.callback_query_handler(text_startswith="refill_payok", state="*")
async def refill_way_yoomoney(call: CallbackQuery, state: FSMContext):
    await state.set_state("here_pay_amount_payok")
    await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")



###################################################################################
#################################### ВВОД СУММЫ ###################################
# Принятие суммы для пополнения средств через QIWI
@dp.message_handler(state="here_pay_amount")
async def refill_get(message: Message, state: FSMContext):
    if message.text.isdigit():
        cache_message = await message.answer("<b>♻ Подождите, платёж генерируется...</b>")
        pay_amount = int(message.text)

        if min_input_qiwi <= pay_amount <= 300000:
            get_way = (await state.get_data())['here_pay_way']
            await state.finish()

            get_message, get_link, receipt = await (
                await QiwiAPI(cache_message, user_bill_pass=True)
            ).bill_pay(pay_amount, get_way)

            if get_message:
                await cache_message.edit_text(get_message, reply_markup=refill_bill_finl(get_link, receipt, get_way))
        else:
            await cache_message.edit_text(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")

@dp.message_handler(state="here_pay_amount_yoomoney")
async def refill_get_yoomoney(message: Message, state: FSMContext):
    if message.text.isdigit():
        cache_message = await message.answer("<b>♻ Подождите, платёж генерируется...</b>")
        pay_amount = int(message.text)

        if min_input_qiwi <= pay_amount <= 300000:
            label = str(message.from_user.id + random.randint(1000, 9999))

            message_url = generate_payment(pay_amount, label)
            message_text =  ded(f"""<b>💰 Пополнение баланса</b>
                               ➖➖➖➖➖➖➖➖➖➖
                               💵 Для пополнения баланса, нажмите на кнопку ниже 
                               <code>Перейти к оплате</code> и оплатите выставленный вам счёт
                               ❗ Время на оплату ограничено.
                               💰 Сумма пополнения: <code>{pay_amount}₽</code>
                               ➖➖➖➖➖➖➖➖➖➖
                               🔄 После оплаты, нажмите на <code>Проверить оплату</code>""")
            await state.finish()
            await cache_message.edit_text(message_text, reply_markup=refill_bill_yoomoney(pay_amount, label, message_url))
        else:
            await cache_message.edit_text(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")

@dp.message_handler(state="here_pay_amount_payok")
async def refill_get_payok(message: Message, state: FSMContext):
    if message.text.isdigit():
        cache_message = await message.answer("<b>♻ Подождите, платёж генерируется...</b>")
        pay_amount = int(message.text)

        if min_input_qiwi <= pay_amount <= 300000:
            label = str(message.from_user.id + random.randint(1000, 9999))
            print(len(label))
            data = get_data_payok()
            print(data)

            message_url = payok_api.createPay(
                secret=data[2],
                amount=pay_amount,
                payment=label,
                shop=int(data[3]),
                desc="Пополнение баланса"

            )
            message_text =  ded(f"""<b>💰 Пополнение баланса</b>
                               ➖➖➖➖➖➖➖➖➖➖
                               💵 Для пополнения баланса, нажмите на кнопку ниже 
                               <code>Перейти к оплате</code> и оплатите выставленный вам счёт
                               ❗ Время на оплату ограничено.
                               💰 Сумма пополнения: <code>{pay_amount}₽</code>
                               ➖➖➖➖➖➖➖➖➖➖
                               🔄 После оплаты, нажмите на <code>Проверить оплату</code>""")
            await state.finish()
            await cache_message.edit_text(message_text, reply_markup=refill_bill_payok(pay_amount, label, message_url))
        else:
            await cache_message.edit_text(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")


###################################################################################
################################ ПРОВЕРКА ПЛАТЕЖЕЙ ################################
# Проверка оплаты через форму
@dp.callback_query_handler(text_startswith="Pay:Form")
async def refill_check_form(call: CallbackQuery):
    receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        await QiwiAPI(call, user_check_pass=True)
    ).check_form(receipt)

    if pay_status == "PAID":
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, "Form", None)
        else:
            await call.answer("❗ Ваше пополнение уже было зачислено.", True)
    elif pay_status == "EXPIRED":
        await call.message.edit_text("<b>❌ Время оплаты вышло. Платёж был удалён.</b>")
    elif pay_status == "WAITING":
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)
    elif pay_status == "REJECTED":
        await call.message.edit_text("<b>❌ Счёт был отклонён.</b>")

#ПРОВЕРКА ПЛАТЕЖА ЮМАНИ
@dp.callback_query_handler(text_startswith="Pay_yoomoney:")
async def refill_check_yoomoney(call: CallbackQuery):
    label = call.data.split(":")[1]
    amount = int(call.data.split(":")[2])
    result =  check_payment(label)
    get_user = get_userx(user_id=call.from_user.id)
    if result == False:
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)
    else:
        receipt = get_receipt()
        await call.message.delete()
        await refill_success(call, receipt, amount, "YooMoney", None)

@dp.callback_query_handler(text_startswith="Pay_payok:")
async def refill_check_payok(call: CallbackQuery):
    label = call.data.split(":")[1]
    amount = int(call.data.split(":")[2])
    result =  check_payment(label)
    get_user = get_userx(user_id=call.from_user.id)

    data = get_data_payok()

    payment_id = call.data.split(":")[1]
    check = payok_api.getTransaction(
            API_ID=data[1],
            API_KEY=data[0],
            shop=int(data[3]),
            payment=payment_id)

    if check['status'] != "success":
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)
    else:
        receipt = get_receipt()
        await call.message.delete()
        await refill_success(call, receipt, amount, "Payok", None)




# Проверка оплаты по переводу (по нику или номеру)
@dp.callback_query_handler(text_startswith=['Pay:Number', 'Pay:Nickname'])
async def refill_check_send(call: CallbackQuery):
    way_pay = call.data.split(":")[1]
    receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        await QiwiAPI(call, user_check_pass=True)
    ).check_send(receipt)

    if pay_status == 1:
        await call.answer("❗ Оплата была произведена не в рублях.", True, cache_time=5)
    elif pay_status == 2:
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)
    elif pay_status == 4:
        pass
    else:
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, way_pay, None)
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)


##########################################################################################
######################################### ПРОЧЕЕ #########################################
# Зачисление средств
async def refill_success(call: CallbackQuery, receipt, amount, get_way, user_id_second):
    if user_id_second == None:
        get_user = get_userx(user_id=call.from_user.id)
    else:
        get_user = get_userx(user_id=user_id_second)

    add_refillx(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt,
                amount, receipt, get_way, get_date(), get_unix())

    if user_id_second == None:
        update_userx(call.from_user.id,
                     user_balance=get_user['user_balance'] + amount,
                     user_refill=get_user['user_refill'] + amount)
        await bot.send_message(call.from_user.id,   f"<b>💰 Вы пополнили баланс на сумму <code>{amount}₽</code>. Удачи ❤\n 🧾 Чек: <code>#{receipt}</code></b>")


    else:
        update_userx(user_id_second,
                     user_balance=get_user['user_balance'] + amount,
                     user_refill=get_user['user_refill'] + amount)

        await bot.send_message(user_id_second,
                               f"<b>💰 Вы пополнили баланс на сумму <code>{amount}₽</code>. Удачи ❤\n 🧾 Чек: <code>#{receipt}</code></b>")

    await send_admins(
        f"👤 Пользователь: <b>@{get_user['user_login']}</b> | <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> | <code>{get_user['user_id']}</code>\n"
        f"💰 Сумма пополнения: <code>{amount}₽</code>\n"
        f"🧾 Чек: <code>#{receipt}</code>"
    )

# Выбор способа пополнения
@dp.callback_query_handler(text="paymanual", state="*")
async def paymanual_way(call: CallbackQuery, state: FSMContext):
    message_text = get_texts('faq')
    await call.message.edit_text(f" <i>Введите желаемую сумму для перевода</i>", reply_markup = paymanual_support())
    await state.set_state("here_pay_amount_paymanual")

@dp.message_handler(state="here_pay_amount_paymanual")
async def paymanual_get(message: Message, state: FSMContext):
    if message.text.isdigit():
        pay_amount = int(message.text)
        if min_input_qiwi <= pay_amount <= 300000:
            await state.set_state("paymanual_finish")
            message_text = get_texts('faq')
            
            # Получение имени пользователя
            username = message.from_user.username
            if not username:
                username = str(message.from_user.id)
                
            await state.update_data(username=username)
            
            await message.answer(ded(f"""<b>Пополнение баланса</b>
                                    ➖➖➖➖➖➖➖➖➖➖
                                    {message_text}
                                    💰 Сумма пополнения: <code>{pay_amount}</code><code>₽</code>
                                    💬 Укажите комментарий: <code>{username}</code>
                                    ➖➖➖➖➖➖➖➖➖➖
                                    🔄 После оплаты, нажмите на кнопку ↓"""),
                                    reply_markup = paymanual_finl(pay_amount, message.from_user.id))
        else:
            await message.answer(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")


@dp.callback_query_handler(text_startswith="paymanual_final:", state="paymanual_finish")
async def paymanual_final(call: CallbackQuery, state: FSMContext):
    pay_amount = int(call.data.split(":")[1])
    id = call.data.split(":")[2]

    async with state.proxy() as data:
        username = data['username']

    if username:
        username_text = f"@{username}"
    else:
        username_text = f"<a href='tg://user?id={call.from_user.id}'>ID: {call.from_user.id}</a>"

    message_text = (f"❓ {username_text} пополнил баланс на <b>{pay_amount}</b> ₽ ❓")

    await send_admins(f"❓ {username_text} пополнил баланс на <b>{pay_amount}</b> ₽ ❓", paymanual_admin_finl(pay_amount, id))
    await state.finish()
    await call.message.edit_text("<b>Успешно</b>")


@dp.callback_query_handler(text_startswith="paymanual_admin:", state="*")
async def paymanual_admin(call: CallbackQuery, state: FSMContext):
    selected = call.data.split(":")[1]
    pay_amount = int(call.data.split(":")[2])

    id = int(call.data.split(":")[3])

    if selected == 'yes':
        receipt = get_receipt()
        await refill_success(call, receipt, pay_amount, "paymanual", id)
    else:
        await bot.send_message(id, "<b>Ваше пополнение отклонили.</b> Если у вас остались вопросы, то обратитесь в техподдержку.")

