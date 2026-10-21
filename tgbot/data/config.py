# - *- coding: utf- 8 - *-
import os
import shutil

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()  # Токен бота
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")

# Папка с данными бота (БД, логи, тексты). В Docker монтируется как volume.
DATA_DIR = os.getenv("DATA_DIR", "tgbot/data")
os.makedirs(DATA_DIR, exist_ok=True)

PATH_DATABASE = os.path.join(DATA_DIR, "database.db")  # Путь к БД
PATH_PROMOCODE = os.path.join(DATA_DIR, "promocode.db")  # Путь к БД промокодов
PATH_LOGS = os.path.join(DATA_DIR, "logs.log")  # Путь к логам
PATH_TEXTS = os.path.join(DATA_DIR, "text.json")  # Тексты FAQ и оплаты (редактируются из бота)

# При первом запуске копируем тексты по умолчанию в папку данных
_DEFAULT_TEXTS = os.path.join(os.path.dirname(__file__), "text.json")
if not os.path.exists(PATH_TEXTS) and os.path.abspath(_DEFAULT_TEXTS) != os.path.abspath(PATH_TEXTS):
    shutil.copyfile(_DEFAULT_TEXTS, PATH_TEXTS)

BOT_VERSION = "3.3"  # Версия бота


# Получение администраторов бота (ADMIN_IDS через запятую)
def get_admins():
    raw = os.getenv("ADMIN_IDS", "")
    return [int(x) for x in raw.replace(" ", "").split(",") if x.strip().isdigit()]


BOT_DESCRIPTION = os.getenv("BOT_DESCRIPTION", "").strip()
