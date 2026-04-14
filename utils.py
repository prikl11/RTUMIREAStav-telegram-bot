from collections import defaultdict
from datetime import date, datetime
from constants import LESSON_EMOJI_LIST, LESSON_TIME_LIST, DAYS
import requests


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