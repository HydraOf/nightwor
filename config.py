# config.py
import os

# На Render добавьте Environment Variable BOT_TOKEN = "токен вашего бота"
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # Телеграм ID живого оператора
