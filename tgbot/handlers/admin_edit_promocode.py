# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from tgbot.data.config import BOT_VERSION, PATH_LOGS, PATH_DATABASE
from tgbot.data.loader import dp
from tgbot.keyboards.reply_all import menu_frep
from tgbot.keyboards.reply_admin_promocode import promocode_edit, promocode_exit, promocode_one_use, promocode_edit_exit, delete_promocode
from tgbot.keyboards.inline_admin_promocode import promocode_delete
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.modules.create_promocode import *
from tgbot.services.sqlite_logic import  *
from tgbot.services.api_sqlite import get_positionx
from tgbot.utils.const_functions import  ded


async def send_info(message, state, promocode, category):
    async with state.proxy() as memory:
        data = get_info(promocode, category)
        if category == "use_count":
            memory['category'] = "use_count"
            await message.answer(f"<b><i>Промокод имеет <code>{data}</code> активаций</i>\n\nВведите новое число актваций</b>", reply_markup=promocode_edit_exit())
        elif category == "discount":
            memory['category'] = "discount"

            position_id = get_info(promocode, "item_position_id")
            info_position = get_positionx(position_id=position_id)
            price = int(info_position['position_price'])
            name_position = info_position['position_name']

            await message.answer(ded(f"""<i>Промокод имеет скидку <b>{data}%</b>.</i>
            
                                 Изначальная цена товара '<b>{name_position}</b>' - <b>{price}₽</b>
                                 Цена с промокодом - <b>{int(price - (price / 100 * data))}₽</b>

                                 Введите новое число скидки"""), reply_markup=promocode_edit_exit())
            
        elif category == "one_use":
            memory['category'] = "one_use"
            if data == 1:
                await message.answer(f"<b><i>Промокод <code>Единоразовый</code>.</i>\n\nСделать его не единоразовым?</b>",  reply_markup=promocode_one_use())
            else:
                await message.answer(f"<b><i>Промокод <code>Не единоразовый</code>.</i>\n\nСделать его единоразовым?</b>",reply_markup=promocode_one_use())
        elif category == "item_position_name" or category == "all_items":
            records = get_all_item()
            message_data = ''
            if records:
                memory['item'] = records
                for character in records:
                    message_data += f"<b><code>{character['position']}</code>. {character['name_item']}</b>\n"
            if category == "item_position_name":
                memory['category'] = "item_position_name"
                info  = get_info(promocode, "all_items")
                if info == 1:
                    await message.answer(f"<b><i>Промокод привязан ко <code>всем товарам</code>.</i>\n\nВведите номер товара, к которому хотите привязать промокод</b>\n\n{message_data}",reply_markup=promocode_edit_exit())
                else:
                    await message.answer(f"<b><i>Промокод привязан к товару:  «<code>{data}</code>».</i>\n\nВведите номер товара, к которому хотите привязать промокод</b>\n\n{message_data}", reply_markup=promocode_edit_exit())
            else:
                if data == 1:
                    await message.answer( f"<b>Данный промокод и так распространяется на все товары</b>",reply_markup=promocode_edit_exit())
                else:
                    memory['category'] = "all_items"
                    data = get_info(promocode, "item_position_name")
                    await message.answer(f"<b><i>Промокод привязан к товару:  «<code>{data}</code>».</i>\n\nРаспространить его на все товары?</b>", reply_markup=promocode_one_use())
        elif category == "promocode":
            memory['category'] = "promocode"
            await message.answer(f"<b>Введите новое название промокода. Оно не должно совпадать с другими промокодами</b>", reply_markup=promocode_edit_exit())


        await EditPromocode.next()






class EditPromocode(StatesGroup):
    item = State()
    change = State()
    edit = State()

#Промокоды
@dp.message_handler(IsAdmin(), text="Управление предыдущими промокодами 📝", state="*")
async def promocode_edit_start(message: Message, state: FSMContext):
    await EditPromocode.item.set()
    records = get_all_promocode()
    message_data = ''
    if records:
        async with state.proxy() as data:
            data['promocode'] = records
        for character in records:
            try:
                item = get_positionx(position_id=character['item_position_id'])
                discount = int(item['position_price'] - (item['position_price'] / 100 * character['discount']))
                price = f"{discount}₽ / {character['discount']}%"

            except TypeError:
                price = f"<b>Отсутствует товар!!</b> / {character['discount']}%"
            if character['name_item'] == None:
                character['name_item'] = "действует на все товары"

            message_data += f"<b><code>{character['position']}</code>. <code>{character['name_promocode']}</code> - {character['name_item']}</b> / {price} \n"
    await message.answer(ded(f"""
    <i><b>Выберите <u>номер</u> промокода, который хотите отредактировать </b></i>
    ➖➖➖➖➖➖➖➖➖➖
    <i>ПРОМОКОД  ➡️  НАЗВАНИЕ ТОВАРА</i>\n{message_data}\n\n"""), reply_markup=promocode_exit())



@dp.message_handler(IsAdmin(), state = EditPromocode.item)
async def promocode_change(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена 🔙":
            await state.finish()
            await message.answer(f"<b>Успешно 👍</b>", reply_markup=menu_frep(message.from_user.id))

        else:
            message_data = False
            for row in data['promocode']:
                if str(row['position']) == message.text:
                    data['promocode_info'] = row
                    message_data = True
            if message_data == True:
                await message.answer(f"<b>Промокод найден!</b>\nВыберите настройку", reply_markup=promocode_edit())
                await EditPromocode.next()
            else:
                await message.answer(f"<b>Промокод к сожалению не найден.\nПовторите попытку!</b>", reply_markup=promocode_exit())
                await EditPromocode.item.set()



@dp.message_handler(IsAdmin(), state = EditPromocode.change)
async def promocode_edit_start(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена 🔙":
            await state.finish()
            await message.answer(f"<b>Успешно 👍</b>", reply_markup=menu_frep(message.from_user.id))
        elif message.text == "Число активаций 🔢":
            await send_info(message, state, data['promocode_info']['name_promocode'], "use_count")
        elif message.text == "Единоразовость 0️⃣":
            await send_info(message, state, data['promocode_info']['name_promocode'], "one_use")
        elif message.text == "Применить промокод для всех товаров 💯":
            await send_info(message, state, data['promocode_info']['name_promocode'], "all_items")
        elif message.text == "Изменить товар для промокода 📦":
            await send_info(message, state, data['promocode_info']['name_promocode'], "item_position_name")
        elif message.text == "Скидку 💵":
            await send_info(message, state, data['promocode_info']['name_promocode'], "discount")
        elif message.text == "Изменить название промокода 🔠":
            await send_info(message, state, data['promocode_info']['name_promocode'], "promocode")
        elif message.text == "Удалить промокод ❌":
            promocode = data['promocode_info']['name_promocode']
            await state.finish()
            await message.answer( f"<b>Вы уверены, что хотите удалить данный промокод?</b>",reply_markup=promocode_delete(promocode))


@dp.message_handler(IsAdmin(), state = EditPromocode.edit)
async def promocode_edit_start(message: Message, state: FSMContext):
    if message.text == "Отмена 🔙":
        await state.finish()
        await message.answer(f"<b>Успешно 👍</b>", reply_markup=menu_frep(message.from_user.id))
    elif message.text == "Назад ⬅":
        await EditPromocode.change.set()
        await message.answer(f"<b>Выберите настройку</b>", reply_markup=promocode_edit())
    else:
        data = False
        async with state.proxy() as memory:
            if memory['category'] == 'discount' or memory['category'] == 'use_count':
                try:
                    info_position = get_positionx(position_id = memory['promocode_info']['item_position_id'])
                    price = int(info_position['position_price'])
                    discount = int(memory['promocode_info']['discount'])
                    int(message.text)
                    data = update_info_discount_count_use(memory['promocode_info']['name_promocode'], memory['category'], message.text)
                    if data:
                        await EditPromocode.change.set()
                        await message.answer(f"<b>Успешно 👍\n\nТовар {info_position['position_name']} будет стоить {int(price - (price / 100 * discount))}₽ </b>", reply_markup=promocode_edit())
                        return
                except ValueError:
                    await message.answer(f"<b>Пожалуйста введите число!</b>", reply_markup=promocode_edit_exit())
                    await EditPromocode.edit.set()
            elif memory['category'] == 'one_use':
                if message.text == "✅":
                    check = get_info(memory['promocode_info']['name_promocode'], memory['category'])
                    if check == 1:
                        value = 0
                    else:
                        value = 1
                    data = update_info_discount_count_use(memory['promocode_info']['name_promocode'], memory['category'], value)
                elif message.text == '❌':
                    await message.answer(f"<b>Выберите настройку</b>", reply_markup=promocode_edit())
                    await EditPromocode.change.set()
            elif memory['category'] == "item_position_name":
                try:
                    for row in memory['item']:
                        if int(message.text) == row['position']:
                            name_item = row['name_item']
                            id_item = row['id_item']
                    data = update_info_items_promocode(memory['promocode_info']['name_promocode'], name_item, id_item)

                except ValueError:
                    await message.answer(f"<b>Пожалуйста введите номер товара!</b>", reply_markup=promocode_edit_exit())
                    await EditPromocode.edit.set()
            elif memory['category'] == "all_items":
                if message.text == "✅":
                    data = update_info_all_items_promocode(memory['promocode_info']['name_promocode'])
                elif message.text == '❌':
                    await message.answer(f"<b>Выберите настройку</b>", reply_markup=promocode_edit())
                    await EditPromocode.change.set()
            elif memory['category'] == "promocode":
                data = update_info_discount_count_use(memory['promocode_info']['name_promocode'], memory['category'], message.text)

        if data:
            await EditPromocode.change.set()
            await message.answer(f"<b>Успешно 👍</b>", reply_markup=promocode_edit())



#Удаление промокодов

@dp.callback_query_handler(IsAdmin(), text_startswith="delete_promocode:", state="*")
async def promocode_delete_start(call: CallbackQuery, state: FSMContext):
    selected = call.data.split(":")[1]
    if selected == 'yes':
        promocode = call.data.split(":")[2]
        delete_promocode_finl(promocode)
        await call.message.answer(ded(f"""
            <b>Успешно!</b>
            ➖➖➖➖➖➖➖➖➖➖➖➖➖➖
            <i>Промокод <code>{promocode}</code> удален! 👍</i>
        """), reply_markup=menu_frep(call.from_user.id))
    elif selected == 'no':
        await call.message.answer("Отменено!", reply_markup = menu_frep(call.from_user.id))