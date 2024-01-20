# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup
from tgbot.data.config import get_admins


# Кнопки назад
def preorder_exit_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Назад 🔙")
    return keyboard

def preorder_select():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("❌ Удалить предзаказ", "✅ Выполнить предзаказ")
    keyboard.row("🏚 В главное меню", "⬅️ Назад")
    return keyboard

def preorder_select_for_load():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("✅", "❌")
    return keyboard