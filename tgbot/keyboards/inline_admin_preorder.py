from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.services.api_sqlite import get_paymentx

# Подтверждение удаления предзакааз
def preorder_edit_delete_finl():
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("❌ Да, удалить", callback_data=f"pre_order_delete:yes"),
        InlineKeyboardButton("✅ Нет, отменить", callback_data=f"pre_order_delete:not")
    )

    return keyboard

def preorder_load_items():
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅", callback_data=f"preorder_load_items:yes"),
        InlineKeyboardButton("❌", callback_data=f"preorder_load_items:not")
    )

    return keyboard
