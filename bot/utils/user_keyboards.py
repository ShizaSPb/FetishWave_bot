from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_only_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="cab:back")]])

def get_cabinet_menu_kb() -> InlineKeyboardMarkup:
    # Примерное меню ЛК (если своего нет). Можно не использовать.
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Мои продукты", callback_data="cab:products")],
    ])
