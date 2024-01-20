from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




def promocode_delete(promocode):
    keyboard= InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅", callback_data=f"delete_promocode:yes:{promocode}"),
        InlineKeyboardButton("❌", callback_data="delete_promocode:no")
    )
    return keyboard