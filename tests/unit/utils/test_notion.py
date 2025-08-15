import os
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime

# Загрузка переменных
load_dotenv()

# Инициализация клиента
notion = Client(auth=os.getenv("NOTION_TOKEN"))


def add_test_record():
    """Добавляет тестовую запись в таблицу"""
    new_page = {
        "Name": {"title": [{"text": {"content": "Test User"}}]},
        "Telegram ID": {"number": 123456789},
        "Username": {"rich_text": [{"text": {"content": "test_user"}}]},
        "Email": {"email": "test@example.com"},
        "Registration Date": {"date": {"start": datetime.now().isoformat()}}
    }

    try:
        response = notion.pages.create(
            parent={"database_id": os.getenv("NOTION_USERS_DB_ID")},
            properties=new_page
        )
        print(f"✅ Запись добавлена! URL: {response['url']}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    # Проверка токена
    token = os.getenv("NOTION_TOKEN")
    print(f"Используемый токен: {'valid' if token else 'missing'}")

    # Добавление записи
    add_test_record()