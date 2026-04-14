from collections import defaultdict
from datetime import date, datetime
import requests
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import os
from dotenv import load_dotenv

from constants import LESSON_EMOJI_LIST, LESSON_TIME_LIST, DAYS
from db import get_user_group_db

load_dotenv()


def _get_schedule_for_range(data: list, start: date, end: date) -> str:
    schedule_by_date = defaultdict(list)
    for lesson in data:
        try:
            lesson_date = datetime.strptime(lesson["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue
        if start <= lesson_date <= end:
            schedule_by_date[lesson["date"]].append(lesson)
        
    if not schedule_by_date:
        return None
    
    output = ""
    for date_str, lessons in sorted(schedule_by_date.items()):
        dt = datetime.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else datetime.combine(date_str, datetime.min.time())
        output += f"\n📅 <b>{DAYS[dt.weekday()]}</b> {dt.strftime('%d.%m')}\n"
        for l in sorted(lessons, key=lambda x: int(x["Para"])):
            time_str = LESSON_TIME_LIST.get(l["Para"])
            emoji_str = LESSON_EMOJI_LIST.get(l["Para"])
            output += f"{emoji_str} {time_str} <b>{l['Disciplina']} ({l['nameDiscVid']})</b> · {l['namePrep']} · <b>{l['nameAud']}</b>\n"

    return output.strip()


def fetch_schedule(id_client: int, id_group: int):
    url = "https://education-ks.ru/getrasp/ajax-dropdown-style"
    params = {
        "method": "getRasp",
        "idClient": id_client,
        "idGroup": id_group,
        "isDo": 0
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://education-ks.ru/getrasp/dropdown-style?idClient={id_client}"
    }

    resp = requests.get(url, params=params, headers=headers)

    try:
        data = resp.json()
    except ValueError:
        return f"Ошибка: сервер вернул некорректный ответ:\n{resp.text[:500]}"

    if not isinstance(data, list):
        return f"Ошибка: ожидался список, а пришло:\n{data}"

    return data, None


def get_user_group(user_id: int):
    user_data = get_user_group_db(user_id)
    if user_data:
        return user_data["group_id"]
    return None


def require_group(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        group_id = get_user_group(update._effective_user.id)
        if not group_id:
            await update.message.reply_text("⚠️ Сначала укажите группу: /group <название группы>")
            return
        return await func(update, context, group_id)
    return wrapper


def require_admin(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != int(os.getenv("ADMIN_ID")):
            return
        return await func(update, context)
    return wrapper

