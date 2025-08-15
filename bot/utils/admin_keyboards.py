from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_payment_actions_kb(payment_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура под уведомлением админу о новом платеже.
    Оставляем только одну кнопку: "Подтвердить оплату".
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"adm_pay:confirm:{payment_id}")],
    ])

def get_admin_confirm_kb(payment_id: str) -> InlineKeyboardMarkup:
    """
    Диалог подтверждения: две кнопки "Да" и "Нет".
    'Нет' просто возвращает к предыдущему экрану (где одна кнопка "Подтвердить оплату").
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Да", callback_data=f"adm_pay:yes:{payment_id}"),
            InlineKeyboardButton("Нет", callback_data=f"adm_pay:no:{payment_id}"),
        ],
    ])
