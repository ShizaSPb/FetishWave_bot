from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.languages import LANGUAGES


def get_language_keyboard():
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES["ru"]["language_name"], callback_data="set_lang_ru")],
        [InlineKeyboardButton(LANGUAGES["en"]["language_name"], callback_data="set_lang_en")]
    ])

def get_welcome_keyboard(lang):
    """Клавиатура приветствия после выбора языка"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["register"], callback_data="start_register")]
    ])

def get_main_menu_keyboard(lang):
    """Клавиатура главного меню с прямой ссылкой"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["products"], callback_data="menu_products")],
        [InlineKeyboardButton(LANGUAGES[lang]["book_session"], callback_data="menu_book_session")],
        [InlineKeyboardButton(LANGUAGES[lang]["buy_ads"], callback_data="menu_buy_ads")],
        [InlineKeyboardButton(LANGUAGES[lang]["offer_cooperation"], callback_data="menu_offer_cooperation")],
        [InlineKeyboardButton(LANGUAGES[lang]["ask_question"], url="https://t.me/Fetishwave_bot")],
        [InlineKeyboardButton(LANGUAGES[lang]["leave_review"], callback_data="menu_leave_review")],
        [InlineKeyboardButton(LANGUAGES[lang]["personal_account"], callback_data="menu_personal_account")]
    ])

def get_products_menu_keyboard(lang):
    """Клавиатура меню продуктов"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["webinars"], callback_data="menu_webinars")],
        [InlineKeyboardButton(LANGUAGES[lang]["consultations"], callback_data="menu_consultations")],
        [InlineKeyboardButton(LANGUAGES[lang]["mentoring"], callback_data="menu_mentoring")],
        [InlineKeyboardButton(LANGUAGES[lang]["page_audit"], callback_data="menu_page_audit")],
        [InlineKeyboardButton(LANGUAGES[lang]["private_channel"], callback_data="menu_private_channel")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="main_menu")]
    ])

def get_webinars_menu_keyboard(lang):
    """Клавиатура меню вебинаров"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_femdom"], callback_data="femdom_webinar")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_joi"], callback_data="webinar_joi")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_psychology"], callback_data="webinar_psychology")],

        [InlineKeyboardButton(LANGUAGES[lang]["webinar_hypno"], callback_data="hypno_webinar")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_sissy"], callback_data="webinar_sissy")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_all_packages"], callback_data="webinar_all_packages")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ])

def get_webinar_details_keyboard(lang, webinar_id):
    """Клавиатура деталей вебинара"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]['buy'], callback_data=f"payment_methods_{webinar_id}")],
        [InlineKeyboardButton(LANGUAGES[lang]['back'], callback_data="menu_webinars")]
    ])

def get_payment_methods_keyboard(lang, webinar_id):
    """Клавиатура выбора способа оплаты"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["payment_rub"], callback_data=f"pay_rub_{webinar_id}")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_crypto"], callback_data=f"pay_crypto_{webinar_id}")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_eur"], callback_data=f"pay_eur_{webinar_id}")],
        [InlineKeyboardButton(LANGUAGES[lang]['back'], callback_data=f"webinar_details_{webinar_id}")]
    ])

def get_back_to_payment_methods_keyboard(webinar_id, lang):
    """Клавиатура с кнопкой возврата к выбору валюты"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["upload_payment_screenshot"], callback_data=f"upload_screenshot:{webinar_id}")],  # Новая кнопка
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data=f"payment_methods_{webinar_id}")]
    ])

def get_private_channel_menu_keyboard(lang):
    """Клавиатура меню приватного канала"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ])

def get_already_registered_keyboard(lang):
    """Клавиатура для уже зарегистрированных пользователей"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["menu_button"], callback_data="main_menu")]
    ])

# ЗДЕСЬ УНИКАЛЬНЫЕ КНОПКИ ДЛЯ ВЕБА С ГИПНОЗОМ

def get_hypno_webinar_keyboard(lang):
    """Клавиатура выбора частей вебинара"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["buy_part1"], callback_data="hypno_part:1")],
        [InlineKeyboardButton(LANGUAGES[lang]["buy_part2"], callback_data="hypno_part:2")],
        [InlineKeyboardButton(LANGUAGES[lang]["buy_both_parts"], callback_data="hypno_part:both")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="back_to_webinars")]
    ])

def get_hypno_payment_keyboard(lang, part):
    """Клавиатура выбора валюты для конкретной части"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["payment_rub"], callback_data=f"hypno_pay:rub:{part}")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_crypto"], callback_data=f"hypno_pay:crypto:{part}")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_eur"], callback_data=f"hypno_pay:eur:{part}")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="back_to_hypno_parts")]
    ])

def get_back_to_hypno_payment_keyboard(lang, part):
    """Клавиатура с кнопкой возврата к выбору валюты"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["upload_payment_screenshot"], callback_data=f"hypno_upload_screenshot:{part}")],  # Новая кнопка
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data=f"hypno_back_to_payment_{part}")]
    ])

# ЗДЕСЬ УНИКАЛЬНЫЕ КНОПКИ ДЛЯ ВЕБА ПО ФЕМДОМУ

def get_femdom_webinar_keyboard(lang):
    """Клавиатура выбора частей вебинара для Femdom"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["buy_part1"], callback_data="femdom_part:1")],
        [InlineKeyboardButton(LANGUAGES[lang]["buy_part2"], callback_data="femdom_part:2")],
        [InlineKeyboardButton(LANGUAGES[lang]["buy_both_parts"], callback_data="femdom_part:both")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="back_to_webinars")]
    ])

def get_femdom_payment_keyboard(lang, part):
    """Клавиатура выбора валюты для конкретной части Femdom"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["payment_rub"], callback_data=f"femdom_pay:rub:{part}")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_crypto"], callback_data=f"femdom_pay:crypto:{part}")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_eur"], callback_data=f"femdom_pay:eur:{part}")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="back_to_femdom_parts")]
    ])

def get_back_to_femdom_payment_keyboard(lang, part):
    """Клавиатура с кнопкой возврата к выбору валюты для Femdom"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["upload_payment_screenshot"], callback_data=f"femdom_upload_screenshot:{part}")],  # Новая кнопка
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data=f"femdom_back_to_payment_{part}")]
    ])

def get_cooperation_keyboard(lang):
    """Клавиатура для раздела сотрудничества"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Заявка" if lang == "ru" else "📝 Application",url="https://forms.gle/YOUR_FORM_LINK")],
        [InlineKeyboardButton("✅ Я заполнил(а)" if lang == "ru" else "✅ I have filled",callback_data="cooperation_filled")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"],callback_data="main_menu")]
    ])

def get_back_to_menu_keyboard(lang):
    """Универсальная клавиатура с кнопкой 'Назад в меню'"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="online_session")]
    ])

def get_consultations_menu_keyboard(lang: str):
    """Клавиатура меню консультаций"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["consultation_personal"], callback_data="consultation_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["consultation_company"], callback_data="consultation_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ])

def get_personal_consultation_keyboard(lang: str):
    """Клавиатура подменю 'Для себя'"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["consultation_love"], callback_data="consultation_type:love")],
        [InlineKeyboardButton(LANGUAGES[lang]["consultation_work"], callback_data="consultation_type:work")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_consultations")]
    ])

def get_company_consultation_keyboard(lang: str):
    """Клавиатура подменю 'Для компании'"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["consultation_employee"], callback_data="consultation_type:employee")],
        [InlineKeyboardButton(LANGUAGES[lang]["consultation_manager"], callback_data="consultation_type:manager")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_consultations")]
    ])

def get_consultation_payment_keyboard(lang: str, consultation_type: str):
    """Клавиатура выбора валюты для консультации"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["payment_rub"], callback_data=f"consultation_pay:rub:{consultation_type}")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_crypto"], callback_data=f"consultation_pay:crypto:{consultation_type}")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_eur"], callback_data=f"consultation_pay:eur:{consultation_type}")],
        [InlineKeyboardButton(LANGUAGES[lang]["upload_payment_screenshot"], callback_data=f"consultation_upload_screenshot:{consultation_type}")],  # Новая кнопка
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data=f"consultation_back:{consultation_type}")]
    ])

def get_back_to_consultation_type_keyboard(lang: str, consultation_type: str):
    """Клавиатура с кнопкой возврата к выбору типа консультации"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            LANGUAGES[lang]["back"],
            callback_data=f"consultation_back:{consultation_type}"
        )]
    ])

def get_back_to_consultation_payment_keyboard(lang: str, consultation_type: str):
    """Клавиатура возврата к выбору валюты"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            LANGUAGES[lang]["back"],
            callback_data=f"consultation_type:{consultation_type}"
        )]
    ])

def get_mentoring_menu_keyboard(lang):
    """Клавиатура меню менторинга"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["mentoring_personal"], callback_data="mentoring_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["mentoring_company"], callback_data="mentoring_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ])

def get_mentoring_keyboard(lang: str, mentoring_type: str):
    """Клавиатура для раздела менторинга"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Заявка" if lang == "ru" else "📝 Application", url="https://forms.gle/YOUR_MENTORING_FORM_LINK")],
        [InlineKeyboardButton("✅ Я заполнил(а)" if lang == "ru" else "✅ I have filled", callback_data=f"mentoring_filled_{mentoring_type}")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_mentoring")]
    ])

def get_mentoring_thanks_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура после отправки заявки на менторинг"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_mentoring")]
    ])

def get_audit_keyboard(lang: str, audit_type: str):
    """Клавиатура для раздела аудита"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["audit_form"], url="https://forms.gle/YOUR_AUDIT_FORM_LINK")],
        [InlineKeyboardButton(LANGUAGES[lang]["audit_form_filled"], callback_data=f"audit_filled_{audit_type}")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_page_audit")]
    ])

def get_page_audit_menu_keyboard(lang):
    """Клавиатура меню аудита страниц"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["audit_personal"], callback_data="audit_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["audit_company"], callback_data="audit_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ])

def get_audit_thanks_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура после отправки заявки на аудит"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_page_audit")]
    ])

def get_buy_ads_keyboard(lang: str):
    """Клавиатура для раздела покупки рекламы"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["buy_ads_form"], url="https://forms.gle/YOUR_ADS_FORM_LINK")],
        [InlineKeyboardButton(LANGUAGES[lang]["buy_ads_form_filled"], callback_data="buy_ads_filled")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="main_menu")]
    ])

def get_buy_ads_thanks_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура после отправки заявки на покупку рекламы"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="main_menu")]
    ])

def get_ask_question_keyboard(lang: str):
    """Клавиатура для раздела 'Задать вопрос'"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["ask_question"], url="https://t.me/Fetishwave_bot")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="main_menu")]
    ])

def get_session_menu_keyboard(lang):
    """Клавиатура меню сессий"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["offline_session"], callback_data="offline_session")],
        [InlineKeyboardButton(LANGUAGES[lang]["online_session"], callback_data="online_session")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="main_menu")]
    ])

def get_offline_session_keyboard(lang):
    """Клавиатура для офлайн сессии"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["session_form"], url="https://forms.gle/YOUR_SESSION_FORM_LINK")],
        [InlineKeyboardButton(LANGUAGES[lang]["session_form_filled"], callback_data="offline_session_filled")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_book_session")]
    ])

def get_online_session_payment_keyboard(lang):
    """Клавиатура выбора валюты для онлайн сессии"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["payment_rub"], callback_data="online_session_payment:rub")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_crypto"], callback_data="online_session_payment:crypto")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_eur"], callback_data="online_session_payment:eur")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="online_session")]
    ])

def get_offline_session_thanks_keyboard(lang):
    """Клавиатура после отправки заявки на офлайн сессию"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_book_session")]
    ])

def get_online_session_keyboard(lang):
    """Клавиатура для онлайн сессии"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["pay_tribute"], callback_data="online_session_payment")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_book_session")]
    ])

def get_back_to_currency_selection_keyboard(lang):
    """Клавиатура для возврата к выбору валюты"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["upload_payment_screenshot"], callback_data="online_session_upload_screenshot")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="online_session_payment")]
    ])

def get_upload_instructions_keyboard(lang: str, back_pattern: str) -> InlineKeyboardMarkup:
    """Клавиатура для экрана загрузки скриншота"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data=back_pattern)]
    ])

def get_success_upload_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура после успешной загрузки скриншота"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back_to_menu"], callback_data="main_menu")]
    ])

def get_invalid_file_keyboard(lang: str, back_pattern: str = 'main_menu') -> InlineKeyboardMarkup:
    """Клавиатура для сообщения о неверном формате файла"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data=back_pattern)]
    ])



def get_donate_currency_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора валюты для доната (идентична разделам оплаты)"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["payment_rub"], callback_data="donate_rub")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_crypto"], callback_data="donate_crypto")],
        [InlineKeyboardButton(LANGUAGES[lang]["payment_eur"], callback_data="donate_eur")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_personal_account")]
    ])
def get_personal_account_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["edit_profile"], callback_data="personal_edit")],
        [InlineKeyboardButton(LANGUAGES[lang]["change_language"], callback_data="personal_change_lang")],
        [InlineKeyboardButton(LANGUAGES[lang]["my_purchases"], callback_data="personal_purchases")],
        [InlineKeyboardButton(LANGUAGES[lang]["donate"], callback_data="menu_donate")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="main_menu")]
    ])

def get_back_to_donate_currency_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Кнопка 'Назад' к выбору валюты доната"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_donate")]
    ])


def get_donate_details_keyboard(lang: str, currency_key: str) -> InlineKeyboardMarkup:
    """
    Клавиатура на экране реквизитов доната:
    1) 📤 Загрузить скриншот оплаты
    2) ◀️ Назад (к выбору валюты доната)
    currency_key: 'rub' | 'crypto' | 'eur'
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["upload_payment_screenshot"], callback_data=f"donate_upload_screenshot:{currency_key}")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_donate")]
    ])


def get_edit_profile_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура меню 'Изменить личные данные'"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["change_name"],  callback_data="personal_edit_name")],
        [InlineKeyboardButton(LANGUAGES[lang]["change_email"], callback_data="personal_edit_email")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"],         callback_data="menu_personal_account")],
    ])
