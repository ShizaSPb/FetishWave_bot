import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
print(f"Токен: {'valid' if token.startswith('secret_') else 'INVALID'} (длина: {len(token)})")

notion = Client(auth=token)
try:
    user = notion.users.me()
    print("Успех! Интеграция:", user['name'])
except Exception as e:
    print("Ошибка:", e)