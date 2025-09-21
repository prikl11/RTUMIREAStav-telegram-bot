from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from schedule_api import get_schedule, get_today_schedule, get_tomorrow_schedule, get_next_week_schedule
import os
from dotenv import load_dotenv
from group_api import get_group_id
from db import init_db, get_user_group_db, read_users, set_user_group_db, get_users_number_by_groups, log_usage, get_command_usage_number, get_count_command_usage, get_usage
import asyncio

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_usage("/start")
    user_data = get_user_group_db(update.effective_user.id)
    if not user_data:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    await update.message.reply_text(
        f"Ваша группа: {user_data['group_name']}\n\n"
        "Команды бота:\n"
        "• /today — расписание на сегодня\n"
        "• /tomorrow — расписание на завтра\n"
        "• /week — расписание на эту неделю\n"
        "• /nextweek — расписание на следующую неделю\n\n"
        "Обратная связь:\nhttps://forms.gle/k1Bvjq5DxR4BQC1U7"
        )

async def set_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_usage("/group")
    if not context.args:
        await update.message.reply_text("Введите /group <название группы>")
        return

    group_name = context.args[0]
    group_id = get_group_id(group_name)

    if not group_id:
        await update.message.reply_text("Такой группы не найдено.")
        return

    set_user_group_db(update.effective_user.id, group_name, group_id)
    await update.message.reply_text(f"Ваша группа сохранена: {group_name}!")

def get_user_group(user_id: int):
    user_data = get_user_group_db(user_id)
    if user_data:
        return user_data["group_id"]
    return None

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_usage("/week")
    group_id = get_user_group(update.effective_user.id)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = get_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_usage("/today")
    group_id = get_user_group(update.effective_user.id)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = get_today_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_usage("/tomorrow")
    group_id = get_user_group(update.effective_user.id)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = get_tomorrow_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_usage("/nextweek")
    group_id = get_user_group(update.effective_user.id)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = get_next_week_schedule(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = int(os.getenv("ADMIN_ID"))
    if update.effective_user.id == admin_id:
        message = f"Количество пользователей: {read_users()}\n"
        users_by_groups = await asyncio.get_event_loop().run_in_executor(None, get_users_number_by_groups)

        message += f"Количество пользователей по группам:\n"
        for group, count in users_by_groups.items():
            message += f"{group}: {count}\n"

        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return

async def commands_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = int(os.getenv("ADMIN_ID"))
    if update.effective_user.id == admin_id:
        message = f"Команд использовано: {get_count_command_usage()}\n"

        message += f"Использование команд:\n"

        usage = await asyncio.get_event_loop().run_in_executor(None, get_command_usage_number)
        for command, count in usage.items():
            message += f"{command}: {count}\n"

        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = int(os.getenv("ADMIN_ID"))
    if update.effective_user.id == admin_id:
        period = context.args[0]
        await update.message.reply_text(f"В течение данного периода использовано команд: {get_usage(period)}")

if __name__ == "__main__":
    init_db()

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("tomorrow", tomorrow))
    app.add_handler(CommandHandler("nextweek", next_week))
    app.add_handler(CommandHandler("group", set_group))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("commands", commands_stats))
    app.add_handler(CommandHandler("usage", usage))

    app.run_polling()