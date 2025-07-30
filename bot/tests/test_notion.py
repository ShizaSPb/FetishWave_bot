from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID
import logging
import sys
from pprint import pformat

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('notion_integration.log')
    ]
)
logger = logging.getLogger(__name__)

# Инициализация клиента (исправленная версия)
try:
    notion = Client(auth=NOTION_TOKEN)  # Убрали timeout_seconds
    logger.info("Notion клиент успешно инициализирован")
except Exception as e:
    logger.critical("Ошибка инициализации Notion клиента: %s", str(e))
    raise


async def add_user_to_notion(user_data: dict):
    """Добавляет пользователя в Notion DB с расширенной валидацией"""
    # Валидация входных данных
    required_fields = ['name', 'telegram_id', 'username', 'reg_date']
    if not all(field in user_data for field in required_fields):
        missing = [f for f in required_fields if f not in user_data]
        logger.error("Отсутствуют обязательные поля: %s", missing)
        return False

    try:
        new_row = {
            "Name": {"title": [{"text": {"content": str(user_data['name'])}}]},
            "Telegram ID": {"number": int(user_data['telegram_id'])},
            "Username": {"rich_text": [{"text": {"content": str(user_data['username'])}}]},
            "Registration Date": {"date": {"start": str(user_data['reg_date'])}}
        }

        logger.debug("Форматированные данные для Notion:\n%s", pformat(new_row))
        logger.info("Попытка создания страницы в БД: %s", NOTION_DATABASE_ID)

        # Проверка существования БД
        try:
            db_info = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
            logger.debug("Информация о БД:\n%s", pformat(db_info))
        except Exception as e:
            logger.error("Ошибка доступа к БД: %s", str(e))
            return False

        # Создание страницы
        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=new_row
        )

        logger.info("Страница успешно создана! ID: %s", response['id'])
        logger.info("URL страницы: %s", response.get('url', 'недоступен'))
        return True

    except ValueError as ve:
        logger.error("Ошибка валидации данных: %s", str(ve))
    except Exception as e:
        logger.error("Неожиданная ошибка при создании страницы: %s", str(e), exc_info=True)

    return False


async def test_connection():
    """Тест подключения к Notion API"""
    try:
        user = notion.users.me()
        logger.info("Успешное подключение к Notion API")
        logger.debug("Информация о пользователе: %s", pformat(user))
        return True
    except Exception as e:
        logger.error("Ошибка подключения к Notion API: %s", str(e))
        return False


if __name__ == "__main__":
    import asyncio


    async def main():
        # Тест подключения
        if not await test_connection():
            sys.exit(1)

        # Тестовые данные
        test_data = {
            "name": "Test User",
            "telegram_id": 12345,
            "username": "test_user",
            "reg_date": "2023-01-01"
        }

        # Вызов основной функции
        result = await add_user_to_notion(test_data)
        logger.info("Результат операции: %s", "Успех" if result else "Неудача")


    asyncio.run(main())