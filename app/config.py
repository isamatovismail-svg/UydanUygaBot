import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8811084936:AAGDkcLRg1IsvrO4K7zURjZsZ4SOkQmhElw")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8371308176"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
