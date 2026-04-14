from datetime import datetime, timedelta

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

