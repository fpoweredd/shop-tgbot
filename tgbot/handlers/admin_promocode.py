# - *- coding: utf- 8 - *-
import aiogram.utils.exceptions
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message
from tgbot.data.config import BOT_VERSION, PATH_LOGS, PATH_DATABASE
from tgbot.data.loader import dp
from tgbot.keyboards.reply_all import menu_frep
from tgbot.keyboards.reply_admin_promocode import promocode_select, promocode_exit,promocode_select_count_use
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.modules.create_promocode import *
from tgbot.services.sqlite_logic import  *
from tgbot.utils.const_functions import  ded

class CreatePromocode(StatesGroup):
    item = State()
    discount = State()
    count_use = State()
    one_use = State()

#Промокоды
@dp.message_handler(IsAdmin(), text="Создать новый промокод 🖍", state="*")
async def promocode_start(message: Message, state: FSMContext):
    await CreatePromocode.item.set()
    records = get_all_item()
    message_data = ''
    if records:
        async with state.proxy() as data:
            data['item'] = records
        for character in records:
            print(character)
            message_data += f"<b><code>{character['position']}</code>. {character['name_item']}. {character['price']}₽ </b>\n"
    try:
        await message.answer(f"<i><b>Выберите <u>номер</u> товара, для которого хотите создать промокод</b></i>\n\n{message_data}", reply_markup=promocode_select())
    except aiogram.utils.exceptions.MessageIsTooLong:
        await message.answer(f"<i><b>Выберите <u>номер</u> товара, для которого хотите создать промокод</b></i>", reply_markup=promocode_select())
        await message.answer(message_data.split('50.')[0])
        await message.answer(message_data.split('50.')[1])
        #TODO колзоз, исрпавить


@dp.message_handler(IsAdmin(), state = CreatePromocode.item)
async def procomode_item(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Выбрать все товары 💯":
            data['all_items'] = 1
            data['item_info'] = None
            await message.answer( f"<i><b>Укажите скидку товаров</b></i>", reply_markup=promocode_exit())
            await CreatePromocode.next()
        elif message.text == "Отмена 🔙":
            await state.finish()
            await message.answer(f"<b>Успешно 👍</b>", reply_markup=menu_frep(message.from_user.id))
        else:
            data['all_items'] = 0
            message_data = False
            for row in data['item']:
                if str(row['position']) == message.text:
                    data['item_info'] = row
                    message_data = True
            if message_data == True:
                await message.answer(f"<b>Товар найден!</b>\nУкажите скидку товара", reply_markup=promocode_exit())
                await CreatePromocode.next()
            else:
                await message.answer(f"<b>Товар к сожалению не найден.\nПовторите попытку!</b>", reply_markup=promocode_exit())
                await CreatePromocode.item.set()

@dp.message_handler(IsAdmin(), state = CreatePromocode.discount)
async def procomode_item(message: Message, state: FSMContext):
    if message.text == "Отмена 🔙":
        await state.finish()
        await message.answer(f"<b>Успешно 👍</b>", reply_markup=menu_frep(message.from_user.id))
    else:
        async with state.proxy() as data:
            discount = message.text
            if "%" in message.text:
                discount = message.text.replace("%", "")
            try:
                int(discount)
                if data['all_items'] == 0:
                    message_data = ded(f"""
                        <b>Новая цена товара составит <code>{int(data['item_info']['price'] - (data['item_info']['price'] / 100 * int(discount)))}</code> ₽</b>
                        <i>Старая цена - <code>{data['item_info']['price']}</code></i> ₽
                        ➖➖➖➖➖➖➖➖➖➖

                        <b>Введите количество использований промокода</b>""")
                else:
                    message_data = "<b>Введите количество использований промокода</b>"

                await message.answer(message_data, reply_markup=promocode_exit())
                data['discount'] = discount
                await CreatePromocode.next()

            except ValueError:
                await message.answer(f"<b>Пожалуйста введите число!</b>",reply_markup=promocode_exit())
                await CreatePromocode.discount.set()

@dp.message_handler(IsAdmin(), state = CreatePromocode.count_use)
async def procomode_count_use(message: Message, state: FSMContext):
    if message.text == "Отмена 🔙":
        await state.finish()
        await message.answer(f"<b>Успешно 👍</b>", reply_markup=menu_frep(message.from_user.id))
    else:
        async with state.proxy() as data:
            data['use_count'] = message.text
        await message.answer(f"<b>Является ль этот промокод единоразовым для пользователя?</b>", reply_markup=promocode_select_count_use())
        await CreatePromocode.next()



@dp.message_handler(IsAdmin(), state = CreatePromocode.one_use)
async def procomode_count_one_use(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена 🔙":
            await state.finish()
            await message.answer(f"<b>Успешно 👍</b>", reply_markup=menu_frep(message.from_user.id))
        elif message.text == "Да" or message.text == "Нет":
            if message.text == "Да":
                data['one_use'] = True

            elif message.text == "Нет":
                data['one_use'] = False
            await message.answer(f"<b>Идет генерация промокода</b>", reply_markup=promocode_exit())
            promocode = create()
            if data['item_info'] == None: #Если выбран пункт, все товары!
                add_promocode(promocode, message.from_user.id, None , None, data['discount'], data['use_count'], data['one_use'], data['all_items'])
            else:
                add_promocode(promocode, message.from_user.id, data['item_info']['name_item'], data['item_info']['id_item'], data['discount'], data['use_count'], data['one_use'], data['all_items'])
            await message.answer(f"Ваш промокод - <b><code>{promocode}</code></b>", reply_markup=menu_frep(message.from_user.id))
            await state.finish()
