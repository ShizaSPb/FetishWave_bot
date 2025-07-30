from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID

notion = Client(
    auth=NOTION_TOKEN,
    notion_version="2022-06-28"  # Добавьте версию API
)

async def add_user_to_notion(user_data: dict):
    try:
        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": user_data["name"]}}]},
                "Telegram ID": {"number": user_data["telegram_id"]}
            }
        )
        print("Успешно создана страница:", response["url"])
        return True
    except Exception as e:
        print("Notion API Error:", e)
        return False

