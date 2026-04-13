from datetime import datetime, timedelta
import requests
from collections import defaultdict

from constants import DAYS, LESSON_EMOJI_LIST, LESSON_TIME_LIST


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

def get_schedule(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client, id_group)
    if error:
        return error

    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_end = start_of_week + timedelta(days=6)

    if today.weekday() == 6:
        return "Сегодня воскресенье😌\nИспользуйте /nextweek, чтобы посмотреть расписание на следующую неделю."

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

    output = ""
    for date_str, lessons in sorted(schedule_by_date.items()):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt.strftime("%d.%m")
        day_name = DAYS[dt.weekday()]

        output += f"\n📅 <b>{day_name}</b> {formatted_date}\n"
        for l in sorted(lessons, key=lambda x: int(x["Para"])):
            time_str = LESSON_TIME_LIST.get(l["Para"])
            emoji_str = LESSON_EMOJI_LIST.get(l["Para"])
            output += f"{emoji_str} {time_str} <b>{l['Disciplina']} ({l['nameDiscVid']})</b> · {l['namePrep']} · <b>{l['nameAud']}</b>\n"

    return output.strip()


def get_today_schedule(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client, id_group)
    if error:
        return error

    today = datetime.today().date()

    today_schedule = []
    for lesson in data:
        try:
            lesson_date = datetime.strptime(lesson["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue

        if lesson_date == today:
            today_schedule.append(lesson)

    if not today_schedule:
        return "Сегодня пар нет 😊"

    day_name = DAYS[today.weekday()]
    formatted_date = today.strftime("%d.%m")

    output = f"📅 <b>{day_name}</b> {formatted_date}\n"
    for l in sorted(today_schedule, key=lambda x: int(x["Para"])):
        time_str = LESSON_TIME_LIST.get(l["Para"])
        emoji_str = LESSON_EMOJI_LIST.get(l["Para"])
        output += f"{emoji_str} {time_str} <b>{l['Disciplina']} ({l['nameDiscVid']})</b> · {l['namePrep']} · <b>{l['nameAud']}</b>\n"

    return output.strip()


def get_tomorrow_schedule(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client, id_group)
    if error:
        return error

    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    tomorrow_schedule = []
    for lesson in data:
        try:
            lesson_date = datetime.strptime(lesson["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue

        if lesson_date == tomorrow:
            tomorrow_schedule.append(lesson)

    if not tomorrow_schedule:
        return "Завтра пар нет 😊"

    day_name = DAYS[tomorrow.weekday()]
    formatted_date = tomorrow.strftime("%d.%m")

    output = f"📅 <b>{day_name}</b> {formatted_date}\n"
    for l in sorted(tomorrow_schedule, key=lambda x: int(x["Para"])):
        time_str = LESSON_TIME_LIST.get(l["Para"])
        emoji_str = LESSON_EMOJI_LIST.get(l["Para"])
        output += f"{emoji_str} {time_str} <b>{l['Disciplina']} ({l['nameDiscVid']})</b> · {l['namePrep']} · <b>{l['nameAud']}</b>\n"

    return output.strip()


def get_next_week_schedule(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client, id_group)
    if error:
        return error

    today = datetime.today().date()
    first_week_start = today - timedelta(days=today.weekday())
    first_week_end = first_week_start + timedelta(days=6)
    second_week_start = first_week_end + timedelta(days=1)
    second_week_end = second_week_start + timedelta(days=6)

    schedule_by_date = defaultdict(list)
    for lesson in data:
        try:
            lesson_date = datetime.strptime(lesson["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue
        if second_week_start <= lesson_date <= second_week_end:
            schedule_by_date[lesson_date].append(lesson)

    if not schedule_by_date:
        return "На следующей неделе нет пар 😊"

    output = ""
    for date_str, lessons in sorted(schedule_by_date.items()):
        if isinstance(date_str, str):
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            dt = date_str

        formatted_date = dt.strftime("%d.%m")
        day_name = DAYS[dt.weekday()]

        output += f"\n📅 <b>{day_name}</b> {formatted_date}\n"
        for l in sorted(lessons, key=lambda x: int(x["Para"])):
            time_str = LESSON_TIME_LIST.get(l["Para"])
            emoji_str = LESSON_EMOJI_LIST.get(l["Para"])
            output += (
                f"{emoji_str} {time_str} "
                f"<b>{l['Disciplina']} ({l['nameDiscVid']})</b> · "
                f"{l['namePrep']} · <b>{l['nameAud']}</b>\n"
            )

    return output.strip()

