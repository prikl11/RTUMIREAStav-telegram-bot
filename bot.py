from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from schedule_api import get_schedule, get_today_schedule
import os
from dotenv import load_dotenv

load_dotenv()

GROUPS = {"СВБО-01-23": 6277}
DEFAULT_GROUP = "СВБО-01-23"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это бот расписания.\n\n"
        "Используйте команду /today, чтобы узнать сегодняшнее расписание,"
        " либо /week для расписания на неделю.\n\n"
        "ℹ️ На данный момент бот поддерживает только группу СВБО-01-23."
    )

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if not context.args:
    #     await update.message.reply_text("Использование: /schedule <название группы>")
    #     return

    # group_name = context.args[0]

    group_id = GROUPS[DEFAULT_GROUP]

    # if not group_id:
    #     await update.message.reply_text("Группа не найдена")
    #     return

    text = get_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = GROUPS[DEFAULT_GROUP]
    text = get_today_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("today", today))

    app.run_polling()