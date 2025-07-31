from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.languages import LANGUAGES
from bot.database.notion_db import get_user_data


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get('lang', 'ru')

    # Проверяем регистрацию
    user_data = await get_user_data(update.effective_user.id)
    if not user_data or user_data.get("status") != "Зарегистрирован":
        await query.answer()
        await query.edit_message_text(
            text=LANGUAGES[lang]["welcome"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(LANGUAGES[lang]["register"], callback_data="start_register")]
            ])
        )
        return

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["products"], callback_data="menu_products")],
        [InlineKeyboardButton(LANGUAGES[lang]["buy_ads"], callback_data="menu_buy_ads")],
        [InlineKeyboardButton(LANGUAGES[lang]["ask_question"], callback_data="menu_ask_question")],
        [InlineKeyboardButton(LANGUAGES[lang]["book_session"], callback_data="menu_book_session")],
        [InlineKeyboardButton(LANGUAGES[lang]["leave_review"], callback_data="menu_leave_review")],
        [InlineKeyboardButton(LANGUAGES[lang]["personal_account"], callback_data="menu_personal_account")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.answer()
        await query.edit_message_text(
            text=LANGUAGES[lang]["main_menu"],
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text=LANGUAGES[lang]["main_menu"],
            reply_markup=reply_markup
        )


async def show_products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get('lang', 'ru')

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["webinars"], callback_data="menu_webinars")],
        [InlineKeyboardButton(LANGUAGES[lang]["consultations"], callback_data="menu_consultations")],
        [InlineKeyboardButton(LANGUAGES[lang]["mentoring"], callback_data="menu_mentoring")],
        [InlineKeyboardButton(LANGUAGES[lang]["page_audit"], callback_data="menu_page_audit")],
        [InlineKeyboardButton(LANGUAGES[lang]["private_channel"], callback_data="menu_private_channel")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_main")]
    ]

    await query.answer()
    await query.edit_message_text(
        text=LANGUAGES[lang]["products"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_submenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get('lang', 'ru')
    menu_type = query.data.split('_')[1]  # Получаем тип меню (consultations, mentoring и т.д.)

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["for_personal"], callback_data=f"menu_{menu_type}_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["for_company"], callback_data=f"menu_{menu_type}_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ]

    await query.answer()
    await query.edit_message_text(
        text=LANGUAGES[lang][menu_type],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# Регистрация обработчиков
handlers = [
    CallbackQueryHandler(show_main_menu, pattern="^menu_main$"),
    CallbackQueryHandler(show_products_menu, pattern="^menu_products$"),
    CallbackQueryHandler(show_submenu, pattern="^menu_(consultations|mentoring|page_audit)$"),
    CallbackQueryHandler(show_main_menu, pattern="^menu_back$")
]