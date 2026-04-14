from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from schedule_api import get_schedule, get_today_schedule, get_tomorrow_schedule, get_next_week_schedule, count_all_lessons
import os
from dotenv import load_dotenv
from group_api import get_group_id
from db import init_db, get_user_group_db, read_users, set_user_group_db, get_users_number_by_groups, log_usage, get_command_usage_number, get_count_command_usage, get_usage, check_meta, update_meta, get_preps_id
import asyncio
from teacher_api import push_preps, get_prep_schedule

load_dotenv()

MAX_LEN = 4000

async def send_long_message(update, text):
    lines = text.split("\n")
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) + 1 > MAX_LEN:
            await update.message.reply_text(chunk, parse_mode=ParseMode.HTML)
            chunk = ""
        chunk += line + "\n"
    if chunk:
        await update.message.reply_text(chunk, parse_mode=ParseMode.HTML)

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
        "• /nextweek — расписание на следующую неделю\n"
        "• /prep <фамилия преподавателя> — расписание преподавателя на неделю\n\n"
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

async def get_teacher_rasp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_usage("/prep")

    if not context.args:
        await update.message.reply_text("Введите /prep <фамилия преподавателя>")
        return

    prep_name = context.args[0]
    prep_id = get_preps_id(prep_name)

    if not prep_id:
        await update.message.reply_text("Такого преподавателя нет")
        return

    text = get_prep_schedule(prep_id)
    await send_long_message(update, text)

async def periodic_update_preps(context: ContextTypes.DEFAULT_TYPE):
    try:
        last_update = check_meta()
        now = datetime.now()

        if last_update:
            last_dt = datetime.fromisoformat(last_update[0])
        else:
            last_dt = datetime(1970, 1, 1)

        if (now - last_dt).days >= 7:
            push_preps()
            update_meta()
    except Exception as e:
        print(f"ERROR: {e}")

async def usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = int(os.getenv("ADMIN_ID"))
    if update.effective_user.id == admin_id:
        period = context.args[0]
        await update.message.reply_text(f"В течение данного периода использовано команд: {get_usage(period)}")


async def count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_usage("/count")
    group_id = get_user_group(update.effective_user.id)
    if not group_id:
        await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
        return

    text = count_all_lessons(id_client=3, id_group=group_id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


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
    app.add_handler(CommandHandler("prep", get_teacher_rasp))
    app.add_handler(CommandHandler("count", count))

    job_queue = app.job_queue
    job_queue.run_repeating(periodic_update_preps, interval=7 * 24 * 60 * 60, first=10)

    app.run_polling()