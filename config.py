import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# IDs отдельных БД в Notion — укажите при желании автоматизировать подтверждение
NOTION_USERS_DB_ID = os.getenv("NOTION_USERS_DB_ID")            # Users
NOTION_PRODUCTS_DB_ID = os.getenv("NOTION_PRODUCTS_DB_ID")      # Products
NOTION_PAYMENTS_DB_ID = os.getenv("NOTION_PAYMENTS_DB_ID")      # Payments
NOTION_PURCHASES_DB_ID = os.getenv("NOTION_PURCHASES_DB_ID")    # Purchases
