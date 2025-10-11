from collections import defaultdict
from datetime import datetime, timedelta
import sqlite3
import requests

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

LESSON_TIME_LIST = {
    "1": "8:15-9:45",
    "2": "9:55-11:25",
    "3": "11:35-13:05",
    "4": "13:30-15:00",
    "5": "15:10-16:40",
    "6": "16:50-18:20"
}

LESSON_EMOJI_LIST = {
    "1": "1️⃣",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
    "5": "5️⃣",
    "6": "6️⃣"
}

def push_preps():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    url = "https://education-ks.ru/getrasp/ajax-dropdown-style"
    params = {
        "method": "getPreps",
        "idClient": 3,
        "isDo": 0
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://education-ks.ru/getrasp/dropdown-style?idClient=3"
    }

    resp = requests.get(url, params=params, headers=headers)
    try:
        data = resp.json()
    except ValueError:
        print("Ошибка: не удалось распарсить JSON.")
        conn.close()
        return

    cursor.executemany(
        "INSERT OR REPLACE INTO preps (prep_id, prep_name) VALUES (?, ?)",
        [(p["idPrep"], p["namePrep"]) for p in data]
    )

    cursor.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES ('preps_last_update', datetime('now'))"
    )

    conn.commit()
    conn.close()

def get_prep_json(id_prep: int):
    url = "https://education-ks.ru/getrasp/ajax-dropdown-style"
    params = {
        "method": "getRaspPrep",
        "idClient": 3,
        "idPrep": id_prep,
        "isDo": 0
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://education-ks.ru/getrasp/dropdown-style?idClient=3"
    }

    resp = requests.get(url, params=params, headers=headers)

    try:
        data = resp.json()
    except ValueError:
        return f"Ошибка: сервер вернул некорректный ответ:\n{resp.text[:500]}"

    if not isinstance(data, list):
        return f"Ошибка: ожидался список, а пришло:\n{data}"

    return data, None

def get_prep_schedule(id_prep: int):
    data, error = get_prep_json(id_prep)
    if error:
        return error

    if not data:
        return "<b>Расписание не найдено</b> (возможно, преподаватель не имеет занятий)."

    prep_name = data[0].get("namePrep", "Неизвестный преподаватель")

    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_end = start_of_week + timedelta(days=6)

    schedule_by_date = defaultdict(list)
    for lesson in data:
        try:
            lesson_date = datetime.strptime(lesson["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue
        if start_of_week <= lesson_date <= week_end:
            schedule_by_date[lesson["date"]].append(lesson)

    if not schedule_by_date:
        return "На этой неделе пар нет 😊"

    output = f"<b>Расписание {prep_name}</b>\n"
    for date_str, lessons in sorted(schedule_by_date.items()):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt.strftime("%d.%m")
        day_name = DAYS[dt.weekday()]

        output += f"\n📅 <b>{day_name}</b> {formatted_date}\n"
        for l in sorted(lessons, key=lambda x: int(x["Para"])):
            para = l["Para"]
            time_str = LESSON_TIME_LIST.get(para, "")
            emoji = LESSON_EMOJI_LIST.get(para, "")
            disc = l.get("Disciplina", "Без названия")
            vid = l.get("nameDiscVid", "")
            group = l.get("nameGroup", "—")
            aud = l.get("nameAud", "—")

            output += f"{emoji} {time_str} — <b>{disc}</b> ({vid})\n · {group} · <i>{aud}</i>\n"

    return output.strip()
