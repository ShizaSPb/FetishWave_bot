from telegram.ext import Application
from config import BOT_TOKEN
from handlers import start, register  # Импортируем обработчики

# Инициализация бота
app = Application.builder().token(BOT_TOKEN).build()

# Регистрируем обработчики команд
app.add_handler(start.handler)  # /start
app.add_handler(register.handler)  # /register

# Запускаем бота
print("Бот запущен!")
app.run_polling()