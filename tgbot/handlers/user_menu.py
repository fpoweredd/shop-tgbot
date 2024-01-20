# - *- coding: utf- 8 - *-
import asyncio
from contextlib import suppress

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import MessageCantBeDeleted
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.data.config import BOT_DESCRIPTION
from tgbot.data.loader import dp
from tgbot.keyboards.inline_all import profile_open_inl
from tgbot.keyboards.inline_page import *
from tgbot.keyboards.inline_user import *
from tgbot.keyboards.reply_all import menu_frep
from tgbot.services.api_sqlite import *
from tgbot.utils.const_functions import get_date, split_messages, get_unix, ded
from tgbot.utils.misc_functions import open_profile_user, upload_text, get_faq, send_admins
from tgbot.services.sqlite_logic import check_promocode, check_use_promocode, used_promocode,used_pre_order, get_id_promocode, get_promocode, update_promocode
# Открытие товаров
@dp.message_handler(text="🎁 Купить", state="*")
async def user_shop(message: Message, state: FSMContext):
    await state.finish()

    if len(get_all_categoriesx()) >= 1:
        await message.answer("<b>🎁 Выберите нужный вам товар:</b>",
                             reply_markup=products_item_category_swipe_fp(0))
    else:
        await message.answer("<b>🎁 Увы, товары в данное время отсутствуют.</b>")


# Открытие профиля
@dp.message_handler(text="👤 Профиль", state="*")
async def user_profile(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(open_profile_user(message.from_user.id), reply_markup=profile_open_inl)


# Проверка товаров в наличии
@dp.message_handler(text="🧮 Наличие товаров", state="*")
async def user_available(message: Message, state: FSMContext):
    await state.finish()

    get_categories = get_all_categoriesx()
    save_items = []

    for category in get_categories:
        get_positions = get_positionsx(category_id=category['category_id'])
        this_items = []

        if len(get_positions) >= 1:
            this_items = [f"<b>➖➖➖ {category['category_name']} ➖➖➖</b>"]

            for position in get_positions:
                get_items = get_itemsx(position_id=position['position_id'])

                if len(get_items) >= 1:
                    this_items.append(
                        f"{position['position_name']} | {position['position_price']}₽ | В наличии {len(get_items)} шт")

        if len(this_items) >= 2:
            save_items.append(this_items)

    if len(save_items) >= 1:
        send_items = ":^^^^^:".join(["\n".join(item) for item in save_items])

        if len(send_items) > 3500:
            split_items = split_messages(send_items.split("\n"), 40)

            for item in split_items:
                await message.answer("\n".join(item).replace(":^^^^^:", "\n\n"))
        else:
            await message.answer("\n\n".join(["\n".join(item) for item in save_items]))
    else:
        await message.answer("<b>🎁 Увы, товары в данное время отсутствуют.</b>")


# Открытие FAQ
@dp.message_handler(text=["ℹ FAQ", "/faq"], state="*")
async def user_faq(message: Message, state: FSMContext):
    await state.finish()

    send_message = get_settingsx()['misc_faq']
    if send_message == "None":
        send_message = f"ℹ Информация. Измените её в настройках бота.\n➖➖➖➖➖➖➖➖➖➖\n{BOT_DESCRIPTION}"

    await message.answer(get_faq(message.from_user.id, send_message), disable_web_page_preview=True)


# Открытие сообщения с ссылкой на поддержку
@dp.message_handler(text=["☎ Поддержка", "/support"], state="*")
async def user_support(message: Message, state: FSMContext):
    await state.finish()

    user_support = get_settingsx()['misc_support']
    if str(user_support).isdigit():
        get_user = get_userx(user_id=user_support)

        if len(get_user['user_login']) >= 1:
            await message.answer("<b>☎ Нажмите кнопку ниже для связи с Администратором.</b>",
                                 reply_markup=user_support_finl(get_user['user_login']))
            return
        else:
            update_settingsx(misc_support="None")

    await message.answer(f"☎ Поддержка. Измените их в настройках бота.\n➖➖➖➖➖➖➖➖➖➖\n{BOT_DESCRIPTION}",
                         disable_web_page_preview=True)


################################################################################################
# Просмотр истории покупок
@dp.callback_query_handler(text="user_history", state="*")
async def user_history(call: CallbackQuery, state: FSMContext):
    last_purchases = last_purchasesx(call.from_user.id, 5)

    if len(last_purchases) >= 1:
        await call.answer("🎁 Последние 5 покупок")
        with suppress(MessageCantBeDeleted):
            await call.message.delete()

        for purchases in last_purchases:
            link_items = await upload_text(call, purchases['purchase_item'])

            await call.message.answer(ded(f"""
                                      <b>🧾 Чек: <code>#{purchases['purchase_receipt']}</code></b>
                                      🎁 Товар: <code>{purchases['purchase_position_name']} | {purchases['purchase_count']}шт | {purchases['purchase_price']}₽</code>
                                      🕰 Дата покупки: <code>{purchases['purchase_date']}</code>
                                      🔗 Товары: <a href='{link_items}'>кликабельно</a>
                                      """))

        await call.message.answer(open_profile_user(call.from_user.id), reply_markup=profile_open_inl)
    else:
        await call.answer("❗ У вас отсутствуют покупки", True)


# Возвращение к профилю
@dp.callback_query_handler(text="user_profile", state="*")
async def user_profile_return(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(open_profile_user(call.from_user.id), reply_markup=profile_open_inl)


################################################################################################
######################################### ПОКУПКА ТОВАРА #######################################
# Переключение страниц категорий для покупки
@dp.callback_query_handler(text_startswith="buy_category_swipe:", state="*")
async def user_purchase_category_next_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🎁 Выберите нужный вам товар:</b>",
                                 reply_markup=products_item_category_swipe_fp(remover))


# Открытие категории для покупки
@dp.callback_query_handler(text_startswith="buy_category_open:", state="*")
async def user_purchase_category_open(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    get_category = get_categoryx(category_id=category_id)
    get_positions = get_positionsx(category_id=category_id)

    if len(get_positions) >= 1:
        with suppress(MessageCantBeDeleted):
            await call.message.delete()

        await call.message.answer(f"<b>🎁 Текущая категория: <code>{get_category['category_name']}</code></b>",
                                  reply_markup=products_item_position_swipe_fp(remover, category_id))
    else:
        if remover == "0":
            await call.message.edit_text("<b>🎁 Увы, товары в данное время отсутствуют.</b>")
            await call.answer("❗ Позиции были изменены или удалены")
        else:
            await call.answer(f"❕ Товары в категории {get_category['category_name']} отсутствуют")


# Открытие позиции для покупки
@dp.callback_query_handler(text_startswith="buy_position_open:", state="*")
async def user_purchase_position_open(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    get_position = get_positionx(position_id=position_id)
    get_category = get_categoryx(category_id=category_id)
    get_items = get_itemsx(position_id=position_id)

    if get_position['position_description'] == "0":
        text_description = ""
    else:
        text_description = f"\n📜 Описание:\n{get_position['position_description']}"

    send_msg = ded(f"""
               <b>🎁 Покупка товара:</b>
               ➖➖➖➖➖➖➖➖➖➖
               🏷 Название: <code>{get_position['position_name']}</code>
               🗃 Категория: <code>{get_category['category_name']}</code>
               💰 Стоимость: <code>{get_position['position_price']}₽</code>
               📦 Количество: <code>{len(get_items)}шт</code>
               {text_description}
               """)

    if len(get_position['position_photo']) >= 5:
        with suppress(MessageCantBeDeleted):
            await call.message.delete()
        await call.message.answer_photo(get_position['position_photo'],
                                        send_msg, reply_markup=products_open_finl(position_id, category_id, remover))
    else:
        await call.message.edit_text(send_msg,
                                     reply_markup=products_open_finl(position_id, category_id, remover))


########################################### АКТИВАЦИЯ ПРОМОКОДА ##########################################

class Promocode(StatesGroup):
    promocode = State()


@dp.callback_query_handler(text_startswith="promocode_position_open:", state="*")
async def user_promocode_start(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])


    async with state.proxy() as data:
        data['position_id'] = position_id
        data['category_id'] = category_id
        data['remover'] = remover
    with suppress(MessageCantBeDeleted):
        await call.message.delete()
    await call.message.answer("<b>Введите промокод</b>", reply_markup=promocode_back(position_id, category_id, remover))
    await Promocode.promocode.set()

@dp.message_handler(state = Promocode.promocode)
async def procomode_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        get_position = get_positionx(position_id=data['position_id'])
        get_category = get_categoryx(category_id=data['category_id'])
        get_items = get_itemsx(position_id=data['position_id'])

        if get_position['position_description'] == "0":
            text_description = ""
        else:
            text_description = f"\n📜 Описание:\n{get_position['position_description']}"
        promocode = False
        check = check_promocode(message.text)
        if len(check) == 0: #Промокода нет в СУБД
            await message.answer("<b>Промокод не найден!</b>", reply_markup = promocode_back(data['position_id'], data['category_id'], data['remover'] ))
        else:
            for i in check:
                position_id = i[3]
                position_name = i[4]
                all_items = i[5]
                discount = i[6]
                use_count = i[7]
                one_use = i[8]
            if position_name == None or position_name == get_position['position_name']:
                check_used = check_use_promocode(message.text)
                if check_used >= 1: #Проверка, есть ль еще активации
                    if one_use == 1: #Промокод единораз
                            check = used_promocode(message.text, message.from_user.id)   #Проверка на единоразовость использользования
                            if check == 0: #Промокод еще не был использован пользователем
                                promocode = True
                            else:
                                send_msg = ded(f"""
                                           <b>🎁 Промокод уже был использован:</b>
                                           ➖➖➖➖➖➖➖➖➖➖
                                           🏷 Название: <code>{get_position['position_name']}</code>
                                           🗃 Категория: <code>{get_category['category_name']}</code>
                                           💰 Стоимость: <code>{get_position['position_price']}₽</code>
                                           📦 Количество: <code>{len(get_items)}шт</code>
                                           {text_description}
                                           """)
                                await message.answer(send_msg,  reply_markup=products_open_finl(data['position_id'], data['category_id'], data['remover'] ))

                    else:
                        promocode = True

                else:
                    send_msg = ded(f"""
                                   <b>🎁 Промокод больше не действует:</b>
                                   ➖➖➖➖➖➖➖➖➖➖
                                   🏷 Название: <code>{get_position['position_name']}</code>
                                   🗃 Категория: <code>{get_category['category_name']}</code>
                                   💰 Стоимость: <code>{get_position['position_price']}₽</code>
                                   📦 Количество: <code>{len(get_items)}шт</code>
                                   {text_description}
                                   """)
                    await message.answer(send_msg, reply_markup=products_open_finl(data['position_id'], data['category_id'],  data['remover']))
            else:
                send_msg = ded(f"""
                           <b>🎁Данный промокод не подходит!:</b>
                           ➖➖➖➖➖➖➖➖➖➖
                           🏷 Название: <code>{get_position['position_name']}</code>
                           🗃 Категория: <code>{get_category['category_name']}</code>
                           💰 Стоимость: <code>{get_position['position_price']}₽</code>
                           📦 Количество: <code>{len(get_items)}шт</code>
                           {text_description}
                           """)
                await message.answer(send_msg, reply_markup=products_open_finl(data['position_id'], data['category_id'], data['remover']))
            if promocode:
                #Высчитывние скидки

                send_msg = ded(f"""
                               <b>🎁 Промокод активирован:</b>
                               ➖➖➖➖➖➖➖➖➖➖
                               🏷 Название: <code>{get_position['position_name']}</code>
                               🗃 Категория: <code>{get_category['category_name']}</code>
                               💰 Стоимость: <code>{int(get_position['position_price'] - (get_position['position_price'] / 100 * discount)) }₽</code>
                               📦 Количество: <code>{len(get_items)}шт</code>
                               {text_description}
                               """)
                promocode_id = get_id_promocode(message.text)
                await message.answer(send_msg,  reply_markup=products_open_finl_after_promocod(data['position_id'], data['category_id'], data['remover'], discount, promocode_id ))


# Переключение страницы позиций для покупки
@dp.callback_query_handler(text_startswith="buy_position_swipe:", state="*")
async def user_purchase_position_next_page(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    get_category = get_categoryx(category_id=category_id)

    await call.message.edit_text(f"<b>🎁 Текущая категория: <code>{get_category['category_name']}</code></b>",
                                 reply_markup=products_item_position_swipe_fp(remover, category_id))




########################################### ПОКУПКА ##########################################


# Выбор количества товаров для покупки
@dp.callback_query_handler(text_startswith="buy_item_open:", state="*")
async def user_purchase_select(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    get_position = get_positionx(position_id=position_id)
    get_items = get_itemsx(position_id=position_id)
    get_user = get_userx(user_id=call.from_user.id)

    try:
        discount = int(call.data.split(":")[3])
        promocode = int(call.data.split(":")[4])
        promocode = get_promocode(promocode)
        price = int(get_position['position_price'] - (get_position['position_price'] / 100 * discount))
    except IndexError:
        discount = None
        promocode = None
        price = int(get_position['position_price'])


    if get_position['position_pre_order'] == 0:
        pre_order_description = ""
    elif get_position['position_pre_order'] == 1:
        pre_order_description = "❕ <b>Внимание! у этой позиции <code>недостающие</code> товары можно предзаказать</b>"


    if price != 0:
        get_count = int(get_user['user_balance'] / price)
        if get_count > len(get_items): get_count = len(get_items)
    else:
        get_count = len(get_items)
    if int(get_user['user_balance']) >= price:
        if get_count >= 1:
            await state.update_data(here_cache_position_id=position_id)
            await state.set_state("here_item_count")
            async with state.proxy() as data:
                data['price'] = price
                data['discount'] = discount
                data['promocode'] = promocode
                data['remover'] = remover
            with suppress(MessageCantBeDeleted):
                await call.message.delete()
            await call.message.answer(ded(f"""
                                      <b>🎁 Введите количество товаров для покупки</b>
                                      ▶ От <code>1</code> до <code>{get_count}</code>
                                      ➖➖➖➖➖➖➖➖➖➖
                                      {pre_order_description}
                                      ➖➖➖➖➖➖➖➖➖➖
                                      🎁 Товар: <code>{get_position['position_name']}</code> - <code>{price}₽</code>
                                      💰 Ваш баланс: <code>{get_user['user_balance']}₽</code>
                                      """))
        else:
            if get_position['position_pre_order'] == 0:
                await call.message.answer("<b>❗ У вас недостаточно средств. 😥</b>",  reply_markup=replenish_user())
            else:
                await call.message.edit_text(ded("""🎁 Товаров нет в наличии
                                               ➖➖➖➖➖➖➖➖➖➖
                                               ▶Желаете ль вы оформить предзаказ?"""), reply_markup=products_pre_order_select(position_id, remover, discount, promocode))

    else:
        await call.message.answer("<b>❗ У вас недостаточно средств. 😥</b>", reply_markup=replenish_user())


# Выбор количества товаров для предзаказа
@dp.callback_query_handler(text_startswith="buy_item_open_preorder:", state="*")
async def user_purchase_pre_order(call: CallbackQuery, state: FSMContext):
    select = call.data.split(":")[1]
    position_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    get_position = get_positionx(position_id=position_id)
    get_items = get_itemsx(position_id=position_id)
    get_user = get_userx(user_id=call.from_user.id)

    try:
        discount = int(call.data.split(":")[4])
        promocode = call.data.split(":")[5]
        price = int(get_position['position_price'] - (get_position['position_price'] / 100 * discount))
    except:
        discount = None
        promocode = None
        price = int(get_position['position_price'])


    if select == "yes":

        if int(get_user['user_balance']) >= price:
            await state.update_data(here_cache_position_id=position_id)
            await state.finish()


            await state.update_data(here_cache_position_id=position_id)
            await state.set_state("here_item_count")
            async with state.proxy() as data:
                data['price'] = price
                data['discount'] = discount
                data['promocode'] = promocode
                data['remover'] = remover

            await call.message.edit_text(ded(f"""
                                      <b>🎁 Введите количество товаров для оформления предзаказа</b>
                                      ➖➖➖➖➖➖➖➖➖➖
                                      🎁 Товар: <code>{get_position['position_name']}</code> - <code>{price}₽</code>
                                      💰 Ваш баланс: <code>{get_user['user_balance']}₽</code>
                                      """))

        else:
            await call.message.answer("<b>❗ У вас недостаточно средств. 😥</b>", reply_markup=replenish_user())

    else:
        await call.message.edit_text("<b>🎁 Выберите нужный вам товар:</b>", reply_markup=products_item_category_swipe_fp(remover))





# Принятие количества товаров для покупки
@dp.message_handler(state="here_item_count")
async def user_purchase_select_count(message: Message, state: FSMContext):
    async with state.proxy() as data:
        price = data['price']
        promocode  = data['promocode']
        remover = data['remover']
    position_id = (await state.get_data())['here_cache_position_id']
    get_position = get_positionx(position_id=position_id)
    get_user = get_userx(user_id=message.from_user.id)
    get_items = get_itemsx(position_id=position_id)


    if price != 0:
        get_count = int(get_user['user_balance'] / price)
        if get_count > len(get_items): get_count = len(get_items)
    else:
        get_count = len(get_items)

    if get_position['position_pre_order'] == 0:
        pre_order_description = ""
    elif get_position['position_pre_order'] == 1:
        pre_order_description = "❕ <b>Внимание! у этой позиции <code>недостающие</code> товары можно предзаказать</b>"

    send_message = ded(f"""
                   ➖➖➖➖➖➖➖➖➖➖
                   🎁 Введите количество товаров для покупки
                   ▶ От <code>1</code> до <code>{get_count}</code>
                   {pre_order_description}
                   ➖➖➖➖➖➖➖➖➖➖
                   🎁 Товар: <code>{get_position['position_name']}</code> - <code>{price}₽</code>
                   💰 Ваш баланс: <code>{get_user['user_balance']}₽</code>
                   """)

    if message.text.isdigit():
        get_count = int(message.text)
        amount_pay = price * get_count

        if len(get_items) >= 1:
            if 1 <= get_count <= len(get_items):
                if int(get_user['user_balance']) >= amount_pay:
                    await state.finish()

                    await message.answer(ded(f"""
                                         <b>🎁 Вы действительно хотите купить товар(ы)?</b>
                                         ➖➖➖➖➖➖➖➖➖➖
                                         🎁 Товар: <code>{get_position['position_name']}</code>
                                         📦 Количество: <code>{get_count}шт</code>
                                         💰 Сумма к покупке: <code>{amount_pay}₽</code>
                                         """),
                                         reply_markup=products_confirm_finl(position_id, get_count, amount_pay, promocode))
                else:
                    await message.answer(f"<b>❌ Недостаточно средств на счете.</b>\n" + send_message, reply_markup=replenish_user())
            else:

                if get_position['position_pre_order'] == 0:
                    await message.answer(f"<b>❌ Неверное количество товаров.</b>\n" + send_message)
                else:
                    await message.answer(ded(f"""🎁 В данный момент доступно <code>{get_count}</code> шт. товара, вы можете получить весь доступный товар сейчас, а остальную часть вашего заказа <code>{(get_count - len(get_items))}</code> шт получить как только появится в наличии
                                                   ➖➖➖➖➖➖➖➖➖➖
                                                   ▶Желаете ль вы оформить предзаказ?"""),
                                                 reply_markup=products_pre_order_confirm(position_id, get_count, price, promocode, remover))
        else:
            if get_position['position_pre_order'] == 0:
                await state.finish()
                await message.answer("<b>🎁 Товар который вы хотели купить, закончился</b>")
            else:
                await message.answer(ded(f"""
                                                         <b>🎁 Вы действительно хотите купить товар(ы)?</b>
                                                         ➖➖➖➖➖➖➖➖➖➖
                                                         🎁 Товар: <code>{get_position['position_name']}</code>
                                                         📦 Количество: <code>{get_count}шт</code>
                                                         💰 Сумма к покупке: <code>{amount_pay}₽</code>
                                                         """),
                                     reply_markup=products_confirm_finl(position_id, get_count, amount_pay, promocode))

    else:
        await message.answer(f"<b>❌ Данные были введены неверно.</b>\n" + send_message)


# Подтверждение покупки товара
@dp.callback_query_handler(text_startswith="pre_order_setup:", state="*")
async def user_purchase_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    position_id = int(call.data.split(":")[2])
    get_count = int(call.data.split(":")[3])
    price = int(call.data.split(":")[4])
    promocode = (call.data.split(":")[5])
    remover = int(call.data.split(":")[6])

    get_position = get_positionx(position_id=position_id)
    get_user = get_userx(user_id=call.from_user.id)

    amount_pay = price * get_count

    if get_action == "yes":
        if int(get_user['user_balance']) >= amount_pay:
            await call.message.edit_text(ded(f"""
                                 <b>🎁 Вы действительно хотите купить товар(ы)?</b>
                                 ➖➖➖➖➖➖➖➖➖➖
                                 🎁 Товар: <code>{get_position['position_name']}</code>
                                 📦 Количество: <code>{get_count}шт</code>
                                 💰 Сумма к покупке: <code>{amount_pay}₽</code>
                                 """),
                                 reply_markup=products_confirm_finl(position_id, get_count, amount_pay, promocode))
        else:
            await call.message.answer("<b>❗ У вас недостаточно средств. 😥</b>", reply_markup=replenish_user())

    else:
        await call.message.edit_text("<b>🎁 Выберите нужный вам товар:</b>", reply_markup=products_item_category_swipe_fp(remover))




# Подтверждение покупки товара
@dp.callback_query_handler(text_startswith="buy_item_confirm:", state="*")
async def user_purchase_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    position_id = int(call.data.split(":")[2])
    get_count = int(call.data.split(":")[3])
    price = int(call.data.split(":")[4])
    promocode = (call.data.split(":")[5])

    if get_action == "yes":
        await call.message.edit_text("<b>🔄 Ждите, товары подготавливаются</b>")

        get_position = get_positionx(position_id=position_id)
        get_items = get_itemsx(position_id=position_id)
        get_user = get_userx(user_id=call.from_user.id)

        amount_pay = price

        if 1 <= int(get_count) <= len(get_items):
            if int(get_user['user_balance']) >= amount_pay:
                save_items, send_count, split_len = buy_itemx(get_items, get_count)

                if get_count != send_count:
                    amount_pay = price
                    get_count = send_count

                receipt = get_unix()
                buy_time = get_date()

                with suppress(MessageCantBeDeleted):
                    await call.message.delete()
                if split_len == 0:
                    await call.message.answer("\n\n".join(save_items), parse_mode="None")
                else:
                    for item in split_messages(save_items, split_len):
                        await call.message.answer("\n\n".join(item), parse_mode="None")
                        await asyncio.sleep(0.3)

                update_userx(get_user['user_id'], user_balance=get_user['user_balance'] - amount_pay)
                add_purchasex(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt, get_count,
                              amount_pay, get_position['position_price'], get_position['position_id'],
                              get_position['position_name'], "\n".join(save_items), buy_time, receipt,
                              get_user['user_balance'], int(get_user['user_balance'] - amount_pay))

                get_items = len(get_itemsx(position_id=position_id)) #Обновление количества товара после покупки
                print(get_items)
                if get_items <= 0:
                    await send_admins(
                        f"👤 Пользователь: <b>@{call.from_user.username} <i>Купил последний товар</i></b>\n"
                        f"💰 Позиция: <code>{get_position['position_name']}</code>\n" )
                try:

                    used_promocode(promocode, call.from_user.id)
                except TypeError:
                    pass
                await call.message.answer(ded(f"""
                                          <b>✅ Вы успешно купили товар(ы)</b>
                                          ➖➖➖➖➖➖➖➖➖➖
                                          🧾 Чек: <code>#{receipt}</code>
                                          🎁 Товар: <code>{get_position['position_name']} | {get_count}шт | {amount_pay}₽</code>
                                          🕰 Дата покупки: <code>{buy_time}</code>
                                          """),
                                          reply_markup=menu_frep(call.from_user.id))
            else:
                await call.message.answer("<b>❗ На вашем счёте недостаточно средств</b>")


        else:
            if get_position['position_pre_order'] == 1:
                if int(get_user['user_balance']) >= amount_pay:
                    save_items, send_count, split_len = buy_itemx(get_items, get_count)

                    if get_count != send_count:
                        amount_pay = price

                    receipt = get_unix()
                    buy_time = get_date()

                    with suppress(MessageCantBeDeleted):
                        await call.message.delete()
                    if split_len == 0:
                        await call.message.answer("\n\n".join(save_items), parse_mode="None")
                    else:
                        for item in split_messages(save_items, split_len):
                            await call.message.answer("\n\n".join(item), parse_mode="None")
                            await asyncio.sleep(0.3)

                    update_userx(get_user['user_id'], user_balance=get_user['user_balance'] - amount_pay)
                    add_purchasex(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt,
                                  get_count,
                                  amount_pay, get_position['position_price'], get_position['position_id'],
                                  get_position['position_name'], "\n".join(save_items), buy_time, receipt,
                                  get_user['user_balance'], int(get_user['user_balance'] - amount_pay))

                    try:
                        update_promocode(promocode, call.from_user.id)
                        used_promocode(promocode, call.from_user.id)
                    except TypeError:
                        pass
                    used_pre_order(call.from_user.id, call.from_user.username, get_position['position_id'], get_position['position_name'], (get_count - len(get_items)) )

                    #Отправка админам
                    await send_admins(
                        f"👤 Пользователь: <b>@{call.from_user.username}</b> | Оформил предзаказ\n"
                        f"💰 Позиция: <code>{get_position['position_name']}</code>\n"
                        f"📦 Количество: <code>{get_count}</code>шт.\n"
                        f"🧾 Товары требуемые для отгрузки: <code>{get_count - len(get_items)}</code>шт."
                    )

                    await call.message.answer(ded(f"""
                                                         <b>✅ Вы успешно купили товар(ы)</b>
                                                         ➖➖➖➖➖➖➖➖➖➖
                                                         🧾 Чек: <code>#{receipt}</code>
                                                         🎁 Товар: <code>{get_position['position_name']} | {get_count}шт | {amount_pay}₽</code>
                                                         🕰 Дата покупки: <code>{buy_time}</code>
                                                         """),
                                              reply_markup=menu_frep(call.from_user.id))
                else:
                    await call.message.answer("<b>❗ На вашем счёте недостаточно средств</b>")

            else:

                await call.message.answer("<b>🎁 Товар который вы хотели купить закончился или изменился.</b>",
                                          reply_markup=menu_frep(call.from_user.id))
    else:
        if len(get_all_categoriesx()) >= 1:
            await call.message.edit_text("<b>🎁 Выберите нужный вам товар:</b>",
                                         reply_markup=products_item_category_swipe_fp(0))
        else:
            await call.message.edit_text("<b>✅ Вы отменили покупку товаров.</b>")

