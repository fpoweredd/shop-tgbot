# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup

from tgbot.data.config import get_admins


# Кнопки главного меню
def promocode_select():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Выбрать все товары 💯", "Отмена 🔙")
    return keyboard


def promocode_exit():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Отмена 🔙")
    return keyboard


def promocode_edit_exit():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Отмена 🔙", 'Назад ⬅')
    return keyboard


def promocode_select_count_use():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Да", "Нет")
    keyboard.row("Отмена 🔙")
    return keyboard

def promocode_edit():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Число активаций 🔢", "Единоразовость 0️⃣")
    keyboard.row("Изменить товар для промокода 📦", "Скидку 💵")
    keyboard.row("Изменить название промокода 🔠","Применить промокод для всех товаров 💯")
    keyboard.row("Удалить промокод ❌")
    keyboard.row("Отмена 🔙")
    return keyboard

def promocode_one_use():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("✅", "❌")
    keyboard.row("Отмена 🔙", 'Назад ⬅')
    return keyboard


def delete_promocode():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("✅", "❌")
    keyboard.row("Отмена 🔙", 'Назад ⬅')
    return keyboard