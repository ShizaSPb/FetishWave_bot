from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notion = Client(auth=NOTION_TOKEN)

async def add_user_to_notion(user_data: dict):
    properties = {
        "Name": {"title": [{"text": {"content": user_data["name"]}}]},
        "Telegram ID": {"number": user_data["telegram_id"]},
        "Username": {"rich_text": [{"text": {"content": user_data.get("username", "")}}]},
        "Email": {"email": user_data["email"]},
        "Registration Date": {"date": {"start": user_data["reg_date"]}}
    }
    # ... (остальной код как ранее)

async def get_user_data(telegram_id: int):
    try:
        response = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={"property": "Telegram ID", "number": {"equals": telegram_id}}
        )
        if response["results"]:
            page = response["results"][0]
            return {
                "name": page["properties"]["Name"]["title"][0]["text"]["content"],
                "email": page["properties"]["Email"]["email"],
                "reg_date": page["properties"]["Registration Date"]["date"]["start"]
            }
        return None
    except Exception as e:
        logger.error(f"Notion query error: {e}")
        return None