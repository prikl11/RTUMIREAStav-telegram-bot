from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from schedule_api import get_schedule, get_today_schedule, get_tomorrow_schedule, get_next_week_schedule
import os
from dotenv import load_dotenv
from group_api import get_group_id

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = context.user_data.get("group_name")
    if not group_name:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    await update.message.reply_text(
        f"Ваша группа: {group_name}\n\n"
        "Команды бота:\n"
        "• /today — расписание на сегодня\n"
        "• /tomorrow — расписание на завтра\n"
        "• /week — расписание на эту неделю\n"
        "• /nextweek — расписание на следующую неделю\n\n"
        )

async def set_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите /group <название группы>")
        return

    group_name = context.args[0]
    group_id = get_group_id(group_name)

    if not group_id:
        await update.message.reply_text("Такой группы не найдено.")
        return

    context.user_data["group_id"] = group_id
    context.user_data["group_name"] = group_name

    await update.message.reply_text(f"Ваша группа сохранена: {group_name}!")

def get_user_group(context: ContextTypes.DEFAULT_TYPE):
    return context.user_data.get("group_id")

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = get_user_group(context)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = get_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = get_user_group(context)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = get_today_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = get_user_group(context)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = get_tomorrow_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = get_user_group(context)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = get_next_week_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("tomorrow", tomorrow))
    app.add_handler(CommandHandler("nextweek", next_week))
    app.add_handler(CommandHandler("group", set_group))

    app.run_polling()