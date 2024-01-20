# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.data.config import BOT_VERSION, PATH_LOGS, PATH_DATABASE
from tgbot.data.loader import dp
from tgbot.keyboards.reply_all import payments_qiwi, settings_frep, functions_frep, items_frep, promoсods_frep, payments_select,payments_yoomoney, admin_back, menu_frep, payments_payok
from tgbot.utils.const_functions import get_date
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.utils.misc_functions import get_statisctics, ded
from tgbot.services.json_logic import get_texts, update_texts


#Промокоды
@dp.message_handler(IsAdmin(), text="♣️ Промокоды", state="*")
async def admin_promokod(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>Панель управления промокодами.</b>", reply_markup=promoсods_frep())


@dp.message_handler(IsAdmin(), text="🥝QIWI", state="*")
async def admin_qiwi(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🔑 Настройка платежных системы.</b>", reply_markup=payments_qiwi())

@dp.message_handler(IsAdmin(), text="💵YooMoney", state="*")
async def admin_yoomoney(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🔑 Настройка платежных системы.</b>", reply_markup=payments_yoomoney())


@dp.message_handler(IsAdmin(), text="🟠Payok", state="*")
async def admin_payok(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🔑 Настройка платежных системы.</b>", reply_markup=payments_payok())

# Платежные системы
@dp.message_handler(IsAdmin(), text="🔑 Платежные системы", state="*")
async def admin_payment(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>Выберите платформу</b>", reply_markup=payments_select())


# Настройки бота
@dp.message_handler(IsAdmin(), text="⚙ Настройки", state="*")
async def admin_settings(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⚙ Основные настройки бота.</b>", reply_markup=settings_frep())


# Общие функции
@dp.message_handler(IsAdmin(), text="🔆 Общие функции", state="*")
async def admin_functions(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🔆 Выберите нужную функцию.</b>", reply_markup=functions_frep(message.from_user.id))


# Управление товарами
@dp.message_handler(IsAdmin(), text="🎁 Управление товарами", state="*")
async def admin_products(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🎁 Редактирование товаров.</b>", reply_markup=items_frep())


# Cтатистики бота
@dp.message_handler(IsAdmin(), text="📊 Статистика", state="*")
async def admin_statistics(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(get_statisctics())


# Получение БД
@dp.message_handler(IsAdmin(), commands=['db', 'database'], state="*")
async def admin_database(message: Message, state: FSMContext):
    await state.finish()

    with open(PATH_DATABASE, "rb") as document:
        await message.answer_document(document,
                                      caption=f"<b>📦 BACKUP\n"
                                              f"🕰 <code>{get_date()}</code></b>")


# Получение Логов
@dp.message_handler(IsAdmin(), commands=['log', 'logs'], state="*")
async def admin_log(message: Message, state: FSMContext):
    await state.finish()

    with open(PATH_LOGS, "rb") as document:
        await message.answer_document(document,
                                      caption=f"<b>🖨 LOGS\n"
                                              f"🕰 <code>{get_date()}</code></b>")


# Получение версии бота
@dp.message_handler(commands=['version', 'log'], state="*")
async def admin_version(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(f"<b>❇ Текущая версия бота: <code>{BOT_VERSION}</code></b>")


#Изменить текст FAQ
@dp.message_handler(IsAdmin(), text="Изменить FAQ", state="*")
async def admin_edit_text(message: Message, state: FSMContext):
    await state.finish()
    message_text = get_texts("faq")
    await state.set_state("change_faq_start")
    await message.answer(ded(f"""
    <b>Прошлый текст сообщения <code>FAQ</code></b>:
    ➖➖➖➖➖➖➖➖➖➖
    <i>{message_text}</i>
    ➖➖➖➖➖➖➖➖➖➖
    <b>Введите новый текст или вернитесь назад</b>
    """), reply_markup = admin_back())


@dp.message_handler(IsAdmin(), state="change_faq_start")
async def admin_edit_text_final(message: Message, state: FSMContext):
    await state.finish()
    if message.text == "⬅ Главное меню":
        await message.answer("<b>Успешно</b>👍", reply_markup = menu_frep(message.from_user.id))
    else:
        update_texts("faq", message.text)
        await message.answer("<b>Успешно</b>👍", reply_markup = menu_frep(message.from_user.id))