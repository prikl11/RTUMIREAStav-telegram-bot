from datetime import datetime, timedelta
from collections import defaultdict

from utils import fetch_schedule, _get_schedule_for_range


def get_schedule(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client, id_group)
    if error:
        return error

    today = datetime.today().date()
    if today.weekday() == 6:
        return "Сегодня воскресенье😌\nИспользуйте /nextweek, чтобы посмотреть расписание на следующую неделю."
    
    start = today - timedelta(days=today.weekday())
    return _get_schedule_for_range(data, start, start + timedelta(days=6)) or "На этой неделе пар нет😊"


def get_today_schedule(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client, id_group)
    if error:
        return error

    today = datetime.today().date()
    return _get_schedule_for_range(data, today, today) or "Сегодня пар нет 😊"


def get_tomorrow_schedule(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client, id_group)
    if error:
        return error
    tomorrow = datetime.today().date() + timedelta(days=1)
    return _get_schedule_for_range(data, tomorrow, tomorrow) or "Завтра пар нет 😊"


def get_next_week_schedule(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client, id_group)
    if error:
        return error
    today = datetime.today().date()
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
    return _get_schedule_for_range(data, start, start + timedelta(days=6)) or "На следующей неделе нет пар 😊"


def count_all_lessons(id_client: int, id_group: int):
    data, error = fetch_schedule(id_client=id_client, id_group=id_group)
    if error:
        return error
    
    today = datetime.today().date()
    end_date = today + timedelta(days=200)
    schedule_by_date = defaultdict(list)
    for lesson in data:
        try:
            lesson_date = datetime.strptime(lesson["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue
        if today <= lesson_date <= end_date:
            schedule_by_date[lesson["date"]].append(lesson)
    
    if not schedule_by_date:
        return "Нет пар 😊"
    
    discipline_counts = defaultdict(lambda: [0, 0, 0])
    for date, lessons_on_date in sorted(schedule_by_date.items()):
        for l in sorted(lessons_on_date, key=lambda x: int(x["Para"])):
            disc = l["Disciplina"]
            if l["nameDiscVid"] == "Лек":
                discipline_counts[disc][0] += 1
            if l["nameDiscVid"] == "Пр":
                discipline_counts[disc][1] += 1
            if l["nameDiscVid"] == "Лаб":
                discipline_counts[disc][2] += 1
    
    sorted_disciplines = sorted(
        discipline_counts.items(),
        key=lambda x: sum(x[1]),
        reverse=True
    )

    lines = ["📚 <b>Оставшиеся пары:</b>\n"]
    for disc, counts in sorted_disciplines:
        parts = []
        if counts[0] > 0:
            parts.append(f"🎓 Лек: <b>{counts[0]}</b>")
        if counts[1] > 0:
            parts.append(f"✏️ Пр: <b>{counts[1]}</b>")
        if counts[2] > 0:
            parts.append(f"🔬 Лаб: <b>{counts[2]}</b>")

        lines.append(f"📖 <b>{disc}</b>")
        lines.append("  " + "  ·  ".join(parts) + "\n")

    return "\n".join(lines).strip()