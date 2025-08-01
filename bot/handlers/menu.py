import logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.languages import LANGUAGES
from bot.database.notion_db import get_user_data
from bot.data.webinar_descriptions import WEBINAR_DESCRIPTIONS


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
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_femdom"], callback_data="webinar_femdom")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_joi"], callback_data="webinar_joi")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_psychology"], callback_data="webinar_psychology")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_hypno"], callback_data="webinar_hypno")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_sissy"], callback_data="webinar_sissy")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ]

    await query.edit_message_text(
        text="🎓 <b>Доступные вебинары:</b>\n\nВыберите интересующий вас вебинар:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.languages import LANGUAGES
from bot.data.webinar_descriptions import WEBINAR_DESCRIPTIONS


async def show_webinar_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получаем язык и ID вебинара
    lang = context.user_data.get('lang', 'ru')
    webinar_id = query.data  # Например: "webinar_femdom"

    # Получаем описание из внешнего файла
    description = WEBINAR_DESCRIPTIONS.get(lang, {}).get(
        webinar_id,
        LANGUAGES[lang].get("default_description", "Описание вебинара недоступно")
    )

    # Формируем клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]['buy'], callback_data=f"payment_methods_{webinar_id}")],
        [InlineKeyboardButton(LANGUAGES[lang]['back'], callback_data="menu_webinars")]
    ]

    # Отправляем сообщение с описанием
    try:
        await query.edit_message_text(
            text=description,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error showing webinar details: {e}")
        await query.edit_message_text(
            text="⚠️ Произошла ошибка при загрузке описания",
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


async def process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    webinar_id = query.data.replace("buy_", "")

    # Здесь реализуйте логику покупки
    await query.edit_message_text(
        text=f"🛒 Оформление покупки вебинара: {webinar_id}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data=webinar_id)]
        ])
    )

async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')
    webinar_id = query.data.replace("payment_methods_", "")

    keyboard = [
        [InlineKeyboardButton("₽ Рубли", callback_data=f"pay_rub_{webinar_id}")],
        [InlineKeyboardButton("₿ Crypto (USDT TRC20)", callback_data=f"pay_crypto_{webinar_id}")],
        [InlineKeyboardButton("€ Euro", callback_data=f"pay_eur_{webinar_id}")],
        [InlineKeyboardButton(LANGUAGES[lang]['back'], callback_data=webinar_id)]
    ]

    await query.edit_message_text(
        text="Выберите способ оплаты:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_rub_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    webinar_id = query.data.replace("pay_rub_", "")

    payment_info = (
        "💳 <b>Оплата в рублях</b>\n\n"
        "Реквизиты для оплаты:\n"
        "Банк: Тинькофф\n"
        "Номер карты: <code>5536 9138 1234 5678</code>\n"
        "Получатель: Иванов И.И.\n\n"
        "После оплаты отправьте чек @username"
    )

    await query.edit_message_text(
        text=payment_info,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data=f"payment_methods_{webinar_id}")]
        ]),
        parse_mode='HTML'
    )


async def show_crypto_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    webinar_id = query.data.replace("pay_crypto_", "")

    payment_info = (
        "₿ <b>Оплата криптовалютой (USDT TRC20)</b>\n\n"
        "Кошелек: <code>TJm...W1f</code>\n"
        "Сеть: TRON (TRC20)\n"
        "Токен: USDT\n\n"
        "После оплаты отправьте хеш транзакции @username"
    )

    await query.edit_message_text(
        text=payment_info,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data=f"payment_methods_{webinar_id}")]
        ]),
        parse_mode='HTML'
    )


async def show_eur_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    webinar_id = query.data.replace("pay_eur_", "")

    payment_info = (
        "€ <b>Оплата в евро</b>\n\n"
        "Реквизиты для оплаты:\n"
        "IBAN: DE89 3704 0044 0532 0130 00\n"
        "BIC: COBADEFFXXX\n"
        "Получатель: Ivanov I.I.\n\n"
        "После оплаты отправьте подтверждение @username"
    )

    await query.edit_message_text(
        text=payment_info,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data=f"payment_methods_{webinar_id}")]
        ]),
        parse_mode='HTML'
    )


# Регистрация обработчиков
handlers = [
    CallbackQueryHandler(show_webinar_details, pattern="^webinar_"),
    CallbackQueryHandler(process_purchase, pattern="^buy_webinar_"),
    CallbackQueryHandler(show_main_menu, pattern="^main_menu$"),
    CallbackQueryHandler(show_products_menu, pattern="^menu_products$"),
    CallbackQueryHandler(show_webinars_menu, pattern="^menu_webinars$"),
    CallbackQueryHandler(show_consultations_menu, pattern="^menu_consultations$"),
    CallbackQueryHandler(show_mentoring_menu, pattern="^menu_mentoring$"),
    CallbackQueryHandler(show_page_audit_menu, pattern="^menu_page_audit$"),
    CallbackQueryHandler(show_private_channel_menu, pattern="^menu_private_channel$"),
    CallbackQueryHandler(show_payment_methods, pattern="^payment_methods_"),
    CallbackQueryHandler(show_rub_payment, pattern="^pay_rub_"),
    CallbackQueryHandler(show_crypto_payment, pattern="^pay_crypto_"),
    CallbackQueryHandler(show_eur_payment, pattern="^pay_eur_"),
]