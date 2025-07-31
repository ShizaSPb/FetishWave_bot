from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.languages import LANGUAGES
from bot.database.notion_db import get_user_data


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get('lang', 'ru')
    user_data = await get_user_data(update.effective_user.id)

    # Если пользователь зарегистрирован
    if user_data and user_data.get("status") == "Зарегистрирован":
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
            await query.edit_message_text(
                text=LANGUAGES[lang]["main_menu"],
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text=LANGUAGES[lang]["main_menu"],
                reply_markup=reply_markup
            )
    else:
        # Если не зарегистрирован
        registration_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(LANGUAGES[lang]["register"], callback_data="start_register")]
        ])

        if query:
            await query.edit_message_text(
                text=LANGUAGES[lang]["registration_required"],
                reply_markup=registration_markup
            )
        else:
            await update.message.reply_text(
                text=LANGUAGES[lang]["registration_required"],
                reply_markup=registration_markup
            )


async def show_products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["webinars"], callback_data="menu_webinars")],
        [InlineKeyboardButton(LANGUAGES[lang]["consultations"], callback_data="menu_consultations")],
        [InlineKeyboardButton(LANGUAGES[lang]["mentoring"], callback_data="menu_mentoring")],
        [InlineKeyboardButton(LANGUAGES[lang]["page_audit"], callback_data="menu_page_audit")],
        [InlineKeyboardButton(LANGUAGES[lang]["private_channel"], callback_data="menu_private_channel")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="main_menu")]
    ]

    await query.edit_message_text(
        text=LANGUAGES[lang]["products"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_webinars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["for_personal"], callback_data="webinars_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["for_company"], callback_data="webinars_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ]

    await query.edit_message_text(
        text=LANGUAGES[lang]["webinars_description"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_consultations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["for_personal"], callback_data="consultations_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["for_company"], callback_data="consultations_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ]

    await query.edit_message_text(
        text=LANGUAGES[lang]["consultations_description"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_mentoring_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["for_personal"], callback_data="mentoring_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["for_company"], callback_data="mentoring_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ]

    await query.edit_message_text(
        text=LANGUAGES[lang]["mentoring_description"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_page_audit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["for_personal"], callback_data="page_audit_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["for_company"], callback_data="page_audit_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ]

    await query.edit_message_text(
        text=LANGUAGES[lang]["page_audit_description"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_private_channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ]

    await query.edit_message_text(
        text=LANGUAGES[lang]["private_channel_description"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# Регистрация обработчиков
handlers = [
    CallbackQueryHandler(show_main_menu, pattern="^main_menu$"),
    CallbackQueryHandler(show_products_menu, pattern="^menu_products$"),
    CallbackQueryHandler(show_webinars_menu, pattern="^menu_webinars$"),
    CallbackQueryHandler(show_consultations_menu, pattern="^menu_consultations$"),
    CallbackQueryHandler(show_mentoring_menu, pattern="^menu_mentoring$"),
    CallbackQueryHandler(show_page_audit_menu, pattern="^menu_page_audit$"),
    CallbackQueryHandler(show_private_channel_menu, pattern="^menu_private_channel$"),
    CallbackQueryHandler(show_main_menu, pattern="^menu_buy_ads$"),
    CallbackQueryHandler(show_main_menu, pattern="^menu_ask_question$"),
    CallbackQueryHandler(show_main_menu, pattern="^menu_book_session$"),
    CallbackQueryHandler(show_main_menu, pattern="^menu_leave_review$"),
    CallbackQueryHandler(show_main_menu, pattern="^menu_personal_account$")
]