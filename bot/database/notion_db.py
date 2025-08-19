from notion_client import Client
from config import NOTION_TOKEN, NOTION_USERS_DB_ID
import logging
from bot.services.actions import log_action
import notion_client.errors
import os


logger = logging.getLogger(__name__)

notion = Client(auth=NOTION_TOKEN)

def _env_clean(key: str):
    v = os.getenv(key)
    if not v:
        return None
    v = v.strip().strip('"').strip("'")
    if v.lower() in ("none", "null", ""):
        return None
    return v

NOTION_TOKEN = _env_clean("NOTION_TOKEN")

# Новые имена + обратная совместимость со старым NOTION_USERS_DB_ID
NOTION_USERS_DB_ID      = _env_clean("NOTION_USERS_DB_ID")      or _env_clean("NOTION_USERS_DB_ID")
NOTION_PRODUCTS_DB_ID   = _env_clean("NOTION_PRODUCTS_DB_ID")
NOTION_PAYMENTS_DB_ID   = _env_clean("NOTION_PAYMENTS_DB_ID")
NOTION_PURCHASES_DB_ID  = _env_clean("NOTION_PURCHASES_DB_ID")


async def add_user_to_notion(user_data: dict) -> str:
    user_id = user_data.get('telegram_id')
    log_action("notion_add_user_attempt", user_id)

    try:
        required_fields = ['telegram_id', 'username', 'language', 'name', 'email', 'status']
        if not all(k in user_data for k in required_fields):
            raise ValueError("Missing required fields")

        response = notion.pages.create(
            parent={"database_id": NOTION_USERS_DB_ID},
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

        log_action("notion_add_user_success", user_id, {
            "page_id": response['id']
        })
        return response['id']
    except Exception as e:
        log_action("notion_add_user_failed", user_id, {
            "error": str(e)
        })
        logger.error(f"Notion create error: {str(e)}", exc_info=True)
        raise


async def update_user_in_notion(page_id: str, update_data: dict) -> bool:
    """
    Частичное обновление пользователя в Notion.
    Принимает любые из ключей: 'name', 'email' и валидно собирает properties.
    Возвращает True/False в зависимости от успешности.
    """
    try:
        properties = {}

        # Title / Name (Notion type: title)
        if 'name' in update_data and update_data['name'] is not None:
            name_val = str(update_data['name']).strip()
            properties["Name"] = {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": name_val}
                    }
                ]
            }

        # Email (Notion type: email)
        if 'email' in update_data and update_data['email'] is not None:
            email_val = str(update_data['email']).strip()
            properties["Email"] = {"email": email_val}

        if not properties:
            logger.warning("update_user_in_notion called with empty properties payload")
            return False

        # Синхронный вызов клиента допустим внутри async
        response = notion.pages.update(
            page_id=page_id,
            properties=properties,
        )
        log_action("notion_update_user_success", update_data.get('telegram_id'), {
            "page_id": page_id,
            "props": list(properties.keys())
        })
        return True

    except notion_client.errors.APIResponseError as e:
        # Ошибки Notion SDK: выведем message и code
        logger.error("Notion update failed: %s (code=%s)", getattr(e, "message", str(e)), getattr(e, "code", None))
        return False
    except Exception as e:
        logger.error("Notion update failed: %s", e, exc_info=True)
        return False


async def get_user_data(telegram_id: int):
    log_action("notion_get_user_attempt", telegram_id)

    try:
        response = notion.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={
                "property": "Telegram ID",
                "number": {"equals": telegram_id}
            }
        )

        if not response["results"]:
            log_action("notion_user_not_found", telegram_id)
            return None

        page = response["results"][0]
        properties = page["properties"]

        user_data = {
            "name": _get_title(properties["Name"]),
            "email": properties["Email"]["email"],
            "status": properties["Status"]["select"]["name"],
            "reg_date": properties["Registration Date"]["date"]["start"],
            "username": _get_rich_text(properties["Username"]),
            "language": properties["Language"]["select"]["name"]
        }

        log_action("notion_get_user_success", telegram_id)
        return user_data
    except Exception as e:
        log_action("notion_get_user_failed", telegram_id, {
            "error": str(e)
        })
        logger.error(f"Notion query error: {e}")
        return None


def _get_title(title_property):
    return title_property["title"][0]["text"]["content"] if title_property["title"] else ""


def _get_rich_text(rich_text_property):
    return rich_text_property["rich_text"][0]["text"]["content"] if rich_text_property["rich_text"] else ""
