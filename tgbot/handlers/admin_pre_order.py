# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from tgbot.data.config import BOT_VERSION, PATH_LOGS, PATH_DATABASE
from tgbot.data.loader import dp
from tgbot.keyboards.reply_all import menu_frep
from tgbot.keyboards.reply_admin_preorder import preorder_exit_menu, preorder_select
from tgbot.keyboards.inline_admin_preorder import preorder_edit_delete_finl
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.modules.create_promocode import *
from tgbot.services.sqlite_logic import  *
from tgbot.services.api_sqlite import get_pre_orderx, get_positionsx
from tgbot.data.loader import bot



class Preorder(StatesGroup):
    select = State()
    edit = State()
    delete = State()
    load_items = State()

@dp.message_handler(IsAdmin(), text="💲 Предзаказы", state="*")
async def pre_order_start(message: Message, state: FSMContext):
    records = get_all_preorder()
    if len(records) == 0:
        await message.answer(f"<i><b>Предзаказов не найдено</b></i>", reply_markup=menu_frep(message.from_user.id))
    else:
        await Preorder.select.set()
        message_data = ''
        if records:
            async with state.proxy() as data:
                data['item'] = records
            for character in records:
                message_data += f"<b><code>{character['position']}</code>. @{character['username']}</b> - {character['item_position_name']} - {character['count']} шт.\n"
        try:
            await message.answer(f"<i><b>Выберите <u>номер</u> предзаказа, который хотите редактировать</b></i>\n\n{message_data}", reply_markup=preorder_exit_menu())
        except aiogram.utils.exceptions.MessageIsTooLong:
            await message.answer(f"<i><b>Выберите <u>номер</u> предзаказа, который хотите редактировать</b></i>",reply_markup=preorder_exit_menu())
            await message.answer(message_data.split('50.')[0])
            await message.answer(message_data.split('50.')[1])
            #TODO колхоз, исправить



@dp.message_handler(IsAdmin(), state = Preorder.select)
async def pre_order_start(message: Message, state: FSMContext):
    if message.text == "Назад 🔙":
        await state.finish()
        await message.answer(f"Успешно 👍", reply_markup=menu_frep(message.from_user.id))
    else:
        async with state.proxy() as data:
            message_data = False
            for row in data['item']:
                if str(row['position']) == message.text:
                    data['user_id'] = row['user_id']
                    data['username'] = row['username']
                    data['item_position_id'] = row['item_position_id']
                    data['item_position_name'] = row['item_position_name']
                    data['count'] = row['count']
                    message_data = True
            if message_data == True:
                await message.answer(f"<b>Предзаказ найден!</b>\nЧто желаете сделать?", reply_markup=preorder_select())
                await Preorder.next()
            else:
                await message.answer(f"<b>Предзаказ к сожалению не найден.\nПовторите попытку!</b>",reply_markup=preorder_exit_menu())
                await Preorder.select.set()


@dp.message_handler(IsAdmin(), state = Preorder.edit)
async def pre_order_edit(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "❌ Удалить предзаказ":
            await message.answer(f"Вы уверены, что хотите удалить предзаказ?", reply_markup=preorder_edit_delete_finl())
            await Preorder.delete.set()
        elif message.text == "✅ Выполнить предзаказ":
            get_positions = get_len_items(data['item_position_id'])
            await message.answer(f"<b>В данный момент есть <code>{len(get_positions)}</code> шт. товара.</b>\n"
                                 "➖➖➖➖➖➖➖➖➖➖\n"
                                 f"<i>Введите количество товара, которого хотите загрузить в предзаказ</i>", reply_markup=preorder_exit_menu())
            await Preorder.load_items.set()
        elif message.text == "⬅️ Назад":
            await message.answer(f"Успешно 👍", reply_markup=preorder_select())
            await Preorder.edit.set()
        elif message.text == "🏚 В главное меню":
            await state.finish()
            await message.answer(f"Успешно 👍", reply_markup=menu_frep(message.from_user.id))


@dp.callback_query_handler(text_startswith="pre_order_delete:", state = Preorder.delete)
async def user_purchase_confirm(call: CallbackQuery, state: FSMContext):
    select = call.data.split(":")[1]

    if select == "yes":
        async with state.proxy() as data:
            delete_pre_order(data['user_id'], data['item_position_id'])
            await call.message.answer(f"Успешно 👍", reply_markup=menu_frep(call.from_user.id))
            await state.finish()
    else:
        await call.message.answer(f"<b></b>\nЧто желаете сделать?", reply_markup=preorder_select())
        await Preorder.edit.set()

@dp.message_handler(IsAdmin(), state=Preorder.load_items)
async def pre_order_edit(message: Message, state: FSMContext):
    if message.text == "Назад 🔙":
        await message.answer(f"Успешно 👍", reply_markup=preorder_select())
        await Preorder.edit.set()
    else:
        async with state.proxy() as data:
            get_positions = get_len_items(data['item_position_id'])
            try:
                count = int(message.text)
                if count > len(get_positions):
                    await message.answer(f"<b>Ошибка</b>\n<i>Превышено количество товаров! Попробуйте еще раз</i>")
                else:
                        if count > data['count']:
                            count = data['count']
                        message_text = ''

                        for i in get_positions[:data['count']]:
                            update_pre_order_(int(data['item_position_id']), data['user_id'],count, i[0])
                            message_text += f"<code>{i[1]}</code>\n\n"

                        await bot.send_message(data['user_id'], f"<b>Вам пришли товары, которые вы предзаказали чуть раньше</b>\n\n{message_text}")
                        await message.answer(f"Успешно 👍", reply_markup=preorder_select())
                        await Preorder.edit.set()
            except ValueError:
                await message.answer(f"<b>Ошибка ввода количества, попробуйте еще раз</b>")
                await Preorder.load_items.set()
