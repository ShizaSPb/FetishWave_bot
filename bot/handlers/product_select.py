"""
Выбор продукта пользователем и сохранение слага в context.user_data["current_payment_type"].
Команда: /products
Кнопки: prod:<slug>
Экспорт: product_select_handlers (для подключения в __init__.py)
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

# === Настрой здесь названия кнопок и соответствующие SLUG-и из Notion.Products ===
PRODUCT_SLUGS = {
    "🎥 Вебинар JOI (demo)": "webinar_joi",
    # "📦 Starter Pack (PDF)": "starter_pack_pdf",
}

def _build_products_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for title, slug in PRODUCT_SLUGS.items():
        rows.append([InlineKeyboardButton(title, callback_data="prod:" + slug)])
    return InlineKeyboardMarkup(rows)

async def cmd_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать выбор продуктов (/products)."""
    kb = _build_products_keyboard()
    if update.effective_message:
        await update.effective_message.reply_text("Выберите продукт для оплаты:", reply_markup=kb)

async def on_pick_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранить выбранный slug в user_data."""
    q = update.callback_query
    if not q or not q.data or not q.data.startswith("prod:"):
        return
    slug = q.data.split(":", 1)[1]
    context.user_data["current_payment_type"] = slug
    await q.answer("Продукт выбран.")
    try:
        await q.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await q.message.reply_text(u"✅ Выбран продукт: {0}\nТеперь отправьте скрин оплаты.".format(slug))

# Экспортируем список хендлеров, чтобы подключить в общем месте
product_select_handlers = [
    CommandHandler("products", cmd_products),
    CallbackQueryHandler(on_pick_product, pattern=r"^prod:"),
]
