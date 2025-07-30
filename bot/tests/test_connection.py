import os
import asyncio
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))

async def test():
    # Проверка подключения
    print("Проверка токена...")
    user = await notion.users.me()
    print(f"Интеграция: {user['name']} ({user['id']})")

    # Проверка базы
    db = await notion.databases.retrieve(database_id=os.getenv("NOTION_DATABASE_ID"))
    print(f"\nБаза: {db['title'][0]['text']['content']}")
    print("Колонки:", list(db["properties"].keys()))

asyncio.run(test())