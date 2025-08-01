from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.languages import LANGUAGES
from bot.database.notion_db import get_user_data


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get('lang', 'ru')
    is_registered = context.user_data.get('registered') or await check_registration(update.effective_user.id)

    if is_registered:
        context.user_data['registered'] = True

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


async def check_registration(user_id: int) -> bool:
    """Проверяет регистрацию в Notion"""
    user_data = await get_user_data(user_id)
    return user_data and user_data.get("status") == "Зарегистрирован"


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
        [InlineKeyboardButton(
            LANGUAGES[lang]["webinar_femdom"],
            url="https://t.me/olga_fetishwave/844"
        )],
        [InlineKeyboardButton(
            LANGUAGES[lang]["webinar_joi"],
            url="https://t.me/olga_fetishwave/263"
        )],
        [InlineKeyboardButton(
            LANGUAGES[lang]["webinar_psychology"],
            url="https://t.me/olga_fetishwave/639"
        )],
        [InlineKeyboardButton(
            LANGUAGES[lang]["webinar_hypno"],
            url="https://t.me/olga_fetishwave/900"
        )],
        [InlineKeyboardButton(
            LANGUAGES[lang]["webinar_sissy"],
            url="https://t.me/olga_fetishwave/1023"
        )],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ]

    await query.edit_message_text(
        text=LANGUAGES[lang]["webinars_title"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
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
    CallbackQueryHandler(show_private_channel_menu, pattern="^menu_private_channel$")
]