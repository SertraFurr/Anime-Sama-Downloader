from datetime import datetime, timedelta

from gui.config import settings


DAY_INDEX = {
    "Lundi": 0, "Mardi": 1, "Mercredi": 2,
    "Jeudi": 3, "Vendredi": 4, "Samedi": 5, "Dimanche": 6
}


def get_domain() -> str:
    return settings.domain


def create_datetime_from_day(day_capitalized, heure, minute):
    day_capitalized = day_capitalized.capitalize()
    if day_capitalized not in DAY_INDEX:
        raise ValueError("Invalid day name.")

    target_index = DAY_INDEX[day_capitalized]

    now = datetime.now()
    current_index = now.weekday()

    days_to_target = target_index - current_index

    target_date = now + timedelta(days=days_to_target)

    return target_date.replace(hour=heure, minute=minute, second=0, microsecond=0)
