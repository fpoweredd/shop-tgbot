# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup
from tgbot.services import sqlite_logic
from tgbot.data.config import get_admins


# Кнопки главного меню
def menu_frep(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🎁 Купить", "👤 Профиль", "🧮 Наличие товаров")
    keyboard.row("☎ Поддержка", "ℹ FAQ")

    if user_id in get_admins():
        keyboard.row("🎁 Управление товарами", "📊 Статистика")
        keyboard.row("⚙ Настройки", "🔆 Общие функции", "🔑 Платежные системы", )
        keyboard.row("♣️ Промокоды", "💲 Предзаказы")

    return keyboard


def payments_select():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🥝QIWI", "💵YooMoney", "🟠Payok")
    keyboard.row( "💵 Переводом 💵",)

    return keyboard


def payments_qiwi():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🥝 Изменить QIWI 🖍", "🥝 Проверить QIWI ♻", "🥝 Баланс QIWI 👁")
    keyboard.row("⬅ Главное меню", "🖲 Способы пополнений")

    return keyboard


def payments_yoomoney():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    data = sqlite_logic.get_check_yoomoney()
    keyboard.row("🥝 Изменить Yoomoney", "🥝 Проверить Yoomoney", "🥝 Баланс YooMoney 👁")
    if data == 'False':
        keyboard.row("✅ Включить Yoomoney")
    else:
        keyboard.row("❌ Выключить Yoomoney")
    keyboard.row("⬅ Главное меню")

    return keyboard

def payments_payok():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    data = sqlite_logic.get_check_payok()
    keyboard.row("🟠 Изменить Payok", "🟠 Проверить Payok", "🟠 Баланс Payok 👁")
    if data == 'False':
        keyboard.row("✅ Включить Payok")
    else:
        keyboard.row("❌ Выключить Payok")
    keyboard.row("⬅ Главное меню")

    return keyboard



# Кнопки управления промокодами
def promoсods_frep():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Создать новый промокод 🖍", "Управление предыдущими промокодами 📝")
    return keyboard


# Кнопки общих функций
def functions_frep(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("👤 Поиск профиля 🔍", "📢 Рассылка", "🧾 Поиск чеков 🔍")
    keyboard.row("⬅ Главное меню")

    return keyboard


# Кнопки настроек
def settings_frep():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🖍 Изменить данные", "🕹 Выключатели")
    keyboard.row("⬅ Главное меню")

    return keyboard

def admin_back():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("⬅ Главное меню")

    return keyboard


# Кнопки изменения товаров
def items_frep():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🎁 Добавить товары ➕", "🎁 Удалить товары 🖍", "🎁 Удалить все товары ❌")
    keyboard.row("📁 Создать позицию ➕", "📁 Изменить позицию 🖍", "📁 Удалить все позиции ❌")
    keyboard.row("🗃 Создать категорию ➕", "🗃 Изменить категорию 🖍", "🗃 Удалить все категории ❌")
    keyboard.row("⬅ Главное меню")

    return keyboard


# Завершение загрузки товаров
finish_load_rep = ReplyKeyboardMarkup(resize_keyboard=True)
finish_load_rep.row("📥 Закончить загрузку товаров")

def payments_paymanual():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    data = sqlite_logic.get_check_paymanual()
    if data == 'False':
        keyboard.row("✅ Включить")
    else:
        keyboard.row("❌ Выключить")
    keyboard.row("⬅ Главное меню", "Изменить FAQ")

    return keyboard
