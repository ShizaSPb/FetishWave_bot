from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.languages import LANGUAGES
import time


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
    """Клавиатура главного меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["products"], callback_data="menu_products")],
        [InlineKeyboardButton(LANGUAGES[lang]["buy_ads"], callback_data="menu_buy_ads")],
        [InlineKeyboardButton(LANGUAGES[lang]["ask_question"], callback_data="menu_ask_question")],
        [InlineKeyboardButton(LANGUAGES[lang]["book_session"], callback_data="menu_book_session")],
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
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_femdom"], callback_data="webinar_femdom")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_joi"], callback_data="webinar_joi")],
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_psychology"], callback_data="webinar_psychology")],
        # Измените эту строку:
        [InlineKeyboardButton(LANGUAGES[lang]["webinar_hypno"], callback_data="hypno_webinar")],  # Было "webinar_hypno"
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
        [InlineKeyboardButton(LANGUAGES[lang]['back'], callback_data=f"webinar_details_{webinar_id}")]  # Изменено на webinar_details_
    ])

def get_back_to_payment_methods_keyboard(webinar_id, lang):
    """Клавиатура с кнопкой возврата к выбору валюты"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data=f"payment_methods_{webinar_id}")]
    ])

def get_consultations_menu_keyboard(lang):
    """Клавиатура меню консультаций"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["for_personal"], callback_data="consultations_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["for_company"], callback_data="consultations_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ])

def get_mentoring_menu_keyboard(lang):
    """Клавиатура меню менторинга"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["for_personal"], callback_data="mentoring_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["for_company"], callback_data="mentoring_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
    ])

def get_page_audit_menu_keyboard(lang):
    """Клавиатура меню аудита страниц"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["for_personal"], callback_data="page_audit_personal")],
        [InlineKeyboardButton(LANGUAGES[lang]["for_company"], callback_data="page_audit_company")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"], callback_data="menu_products")]
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
        [InlineKeyboardButton(LANGUAGES[lang]["back"],
         callback_data=f"hypno_back_to_payment_{part}")]
    ])