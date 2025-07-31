from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notion = Client(auth=NOTION_TOKEN)

async def add_user_to_notion(user_data: dict) -> str:
    """Создание записи с возвратом page_id"""
    try:
        required_fields = ['telegram_id', 'username', 'language', 'name', 'email', 'status']
        if not all(k in user_data for k in required_fields):
            raise ValueError("Missing required fields")

        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": user_data["name"]}}]},
                "Telegram ID": {"number": user_data["telegram_id"]},
                "Username": {"rich_text": [{"text": {"content": user_data["username"]}}]},
                "Language": {"select": {"name": user_data["language"]}},
                "Email": {"email": user_data["email"]},
                "Status": {"select": {"name": user_data["status"]}},
                "Registration Date": {"date": {"start": user_data["reg_date"]}}
            }
        )
        return response['id']
    except Exception as e:
        logger.error(f"Notion create error: {str(e)}", exc_info=True)
        raise

async def update_user_in_notion(page_id: str, update_data: dict):
    """Обновление записи с расширенной обработкой ошибок"""
    properties = {
        "Name": {"title": [{"text": {"content": update_data["name"]}}]},
        "Email": {"email": update_data["email"]}
    }

    try:
        if not all([update_data.get('name'), update_data.get('email')]):
            raise ValueError("Missing required fields")

        response = notion.pages.update(
            page_id=page_id,
            properties=properties
        )

        if not response.get('id'):
            raise Exception("Notion returned empty response")

        return True
    except Exception as e:
        logger.error(f"Notion update failed: {e}", exc_info=True)
        return False

async def get_user_data(telegram_id: int):
    """Получаем данные пользователя по Telegram ID"""
    try:
        response = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={
                "property": "Telegram ID",
                "number": {"equals": telegram_id}
            }
        )

        if not response["results"]:
            return None

        page = response["results"][0]
        properties = page["properties"]

        return {
            "name": _get_title(properties["Name"]),
            "email": properties["Email"]["email"],
            "status": properties["Status"]["select"]["name"],
            "reg_date": properties["Registration Date"]["date"]["start"],
            "username": _get_rich_text(properties["Username"]),
            "language": properties["Language"]["select"]["name"]
        }
    except Exception as e:
        logger.error(f"Notion query error: {e}")
        return None

def _get_title(title_property):
    return title_property["title"][0]["text"]["content"] if title_property["title"] else ""

def _get_rich_text(rich_text_property):
    return rich_text_property["rich_text"][0]["text"]["content"] if rich_text_property["rich_text"] else ""